"""Graphene resolvers look like classes but are actually metaprogram-y resolver interfaces.
Each resolver describes how a graphql response can be resolved from some 'root' data structure.
This isn't super intuitive and at the moment is not very well documented.

We can have something like:
>>> import json
>>> from typing import NamedTuple
>>> import graphene
>>>
>>> class PersonNamedTuple(NamedTuple):
...     first_name: str
...     last_name: str
>>>
>>> class PersonGraphQl(graphene.ObjectType):
...     first_name = graphene.String()
...     last_name = graphene.String()
...     full_name = graphene.String()
...
...     def resolve_full_name(root: PersonNamedTuple, info) -> str:  # root is a PersonNamedTuple.
...         return root.first_name + ' ' + root.last_name
>>>
>>> class Query(graphene.ObjectType):
...     person = graphene.Field(PersonGraphQl)  # `person` is a PersonGraphQl type.
...
...     # But its resolver returns a PersonNamedTuple.
...     def resolve_person(root, info) -> PersonNamedTuple:
...         return PersonNamedTuple('Michael', 'Jackson')
>>>
>>> result = graphene.Schema(query=Query).execute('''
... query person {
...   person {
...     firstName
...     lastName
...     fullName
...   }
... }
... ''')
>>>
>>> print(json.dumps(result.data))
{"person": {"firstName": "Michael", "lastName": "Jackson", "fullName": "Michael Jackson"}}

It's a little funky, and even funkier for the relay pagination stuff.

From the docs:
'NOTE: The resolvers on a ObjectType are always treated as staticmethods, so the first argument to
the resolver method self (or root) need not be an actual instance of the ObjectType.'
"""
from datetime import date, datetime
from typing import List, Optional

import graphene

from graphql import ResolveInfo

from front import use_listens, use_sunlight_windows
from front.definitions import Listen, ListenInput, MusicProvider, Song, SortOrder, SunlightWindow
from front.delivery.graphql.util import RelayPaginationArguments, build_page_info


GraphQlMusicProvider = graphene.Enum.from_enum(MusicProvider)


class GraphQlSong(graphene.ObjectType):
    """A song from a given music provider."""
    class Meta:
        name = 'Song'

    id = graphene.ID(required=True)
    name = graphene.String()
    song_provider = GraphQlMusicProvider()
    artist_name = graphene.String()
    album_name = graphene.String()
    image_large_url = graphene.String()
    image_medium_url = graphene.String()
    image_small_url = graphene.String()

    def resolve_image_large_url(root: Song, info: ResolveInfo) -> str:
        return root.image_url_by_size['large']

    def resolve_image_medium_url(root: Song, info: ResolveInfo) -> str:
        return root.image_url_by_size['medium']

    def resolve_image_small_url(root: Song, info: ResolveInfo) -> str:
        return root.image_url_by_size['small']


class GraphQlListen(graphene.ObjectType):
    """A listen submitted by a user to morning cd."""
    class Meta:
        name = 'Listen'

    id = graphene.ID(required=True)
    song = graphene.Field(GraphQlSong)
    listener_name = graphene.String()
    listen_time_utc = graphene.DateTime()
    note = graphene.String()
    iana_timezone = graphene.String()

    def resolve_song(root: Listen, info: ResolveInfo) -> Song:
        return use_listens.get_song_of_listen(info.context, root)


class ListenConnection(graphene.relay.Connection):
    """A collection of listens from morning cd with relay cursor-pagination."""
    class Meta:
        node = GraphQlListen

    class Edge:
        node = GraphQlListen()
        cursor = graphene.DateTime()


class GraphQlSunlightWindow(graphene.ObjectType):
    """The sunrise and sunset utc times for a location on a given date."""
    class Meta:
        name = 'SunlightWindow'

    sunrise_utc = graphene.DateTime(required=True)
    sunset_utc = graphene.DateTime(required=True)


class Query(graphene.ObjectType):
    """Root query type for morning cd."""
    listen = graphene.Field(GraphQlListen, args={'id': graphene.ID(required=True)})

    all_listens = graphene.relay.ConnectionField(
        ListenConnection,
        before=graphene.DateTime(),
        after=graphene.DateTime()
    )

    sunlight_window = graphene.Field(GraphQlSunlightWindow, args={
        'iana_timezone': graphene.String(required=True),
        'on_date': graphene.Date(required=True)
    })

    def resolve_listen(root, info: ResolveInfo, id: str) -> Listen:
        return use_listens.get_listen(info.context, id)

    def resolve_all_listens(root,
                            info: ResolveInfo,
                            before: Optional[datetime] = None,
                            after: Optional[datetime] = None,
                            first: Optional[int] = None,
                            last: Optional[int] = None) -> ListenConnection:
        """Resolver for allListens that returns a ListenConnection. Graphene is super confusing
        and therefore so is this (at the moment).
        """
        pagination_args = RelayPaginationArguments.make_relay_pagination_arguments(
            first=first,
            last=last,
            before=before,
            after=after
        )

        # if we're getting the first n listens, we'll just get listens limit `first` in ascending
        # order. if we're getting the last n listens, we'll get listens limit `last` in descending
        # order, then reverse that output. "is it worth it? let me work it. i put my thing down,
        # flip it and reverse it."
        sort_order = SortOrder.DESCENDING if pagination_args.last_is_set else SortOrder.ASCENDING
        limit = pagination_args.first if pagination_args.first_is_set else pagination_args.last

        listens_plus_one = use_listens.get_listens(
            info.context,
            before_utc=before,
            after_utc=after,
            sort_order=sort_order,
            limit=limit + 1  # + 1, to see if the db 'has more'
        )
        has_more = len(listens_plus_one) == limit + 1
        listens = listens_plus_one[:limit]

        if pagination_args.last_is_set:
            listens = list(reversed(listens))

        return Query._build_listen_connection(listens, has_more, pagination_args)

    def _build_listen_connection(listens: List[Listen],
                                 has_more: bool,
                                 pagination_args: RelayPaginationArguments) -> ListenConnection:
        return ListenConnection(
            edges=Query._build_listen_edges(listens),
            page_info=build_page_info(has_more, pagination_args)
        )

    def _build_listen_edges(listens: List[Listen]) -> List[ListenConnection.Edge]:
        return [ListenConnection.Edge(node=listen, cursor=listen.listen_time_utc)  # type: ignore
                for listen in listens]

    def resolve_sunlight_window(root,
                                info: ResolveInfo,
                                iana_timezone: str,
                                on_date: date) -> SunlightWindow:
        return use_sunlight_windows.get_sunlight_window(
            info.context,
            iana_timezone,
            on_date=on_date
        )


class GraphQlListenInput(graphene.InputObjectType):
    """Input for submitting a listen to morning cd."""
    class Meta:
        name = 'ListenInput'

    song_id = graphene.String(required=True)
    song_provider = GraphQlMusicProvider(default_value=GraphQlMusicProvider.SPOTIFY.value)
    listener_name = graphene.String(required=True)
    note = graphene.String(required=False)
    iana_timezone = graphene.String(required=True)


class SubmitListen(graphene.Mutation):
    """Mutation for submitting a listen to morning cd. Listens must be submitted during daytime."""
    class Arguments:
        input = GraphQlListenInput(required=True)

    Output = GraphQlListen

    def mutate(root, info: ResolveInfo, input: GraphQlListenInput) -> Listen:
        listen = ListenInput(
            song_id=input.song_id,
            song_provider=MusicProvider(input.song_provider),
            listener_name=input.listener_name,
            note=input.note,
            iana_timezone=input.iana_timezone
        )
        return use_listens.submit_listen(info.context, listen)


class Mutation(graphene.ObjectType):
    """Root mutation type for morning cd."""
    submit_listen = SubmitListen.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
