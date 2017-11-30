from .abcs import Messageable


class Message(Messageable):

    def __init__(self, **attrs):
        self._author = attrs.pop('author', None)
        self._channel = attrs.pop('channel', None)
        self._raw_data = attrs.pop('raw_data', None)
        self._writer = attrs.pop('_writer', None)
        self.content = attrs.pop('content', None)
        self.clean_content = attrs.pop('clean_content', None)
        self._tags = attrs.pop('tags', None)
        try:
            self._timestamp = self.tags['sent-ts']
        except KeyError:
            self._timestamp = self.tags['tmi-sent-ts']

    def __repr__(self):
        return '<Message author={0.author} channel={0.channel}>'.format(self)

    async def _get_channel(self):
        return self.channel, None

    async def _get_writer(self):
        return self._writer

    async def _get_method(self):
        return self.__class__.__name__

    @property
    def author(self):
        """The User object associated with the Message."""
        return self._author

    @property
    def channel(self):
        """The Channel object associated with the Message."""
        return self._channel

    @property
    def raw_data(self):
        """The raw data received from Twitch for this Message."""
        return self._raw_data

    @property
    def tags(self):
        """The tags associated with the Message.

        Could be None."""
        return self._tags

    @property
    def timestamp(self):
        """The Twitch timestamp for this Message."""
        return self._timestamp


class Channel(Messageable):

    def __init__(self, name, _writer, _http):
        self._channel = name
        self._writer = _writer
        self._http = _http

    def __repr__(self):
        return self._channel

    @property
    def name(self):
        """The channel name."""
        return self._channel

    async def _get_channel(self):
        return self.name, None

    async def _get_writer(self):
        return self._writer

    async def _get_method(self):
        return self.__class__.__name__

    async def get_stream(self):
        """|coro|

        Method which retrieves stream information on the channel, provided it is active(Live).

        Returns
        ---------
        dict
            Dict containing active streamer data. Could be None if the stream is not live.

        Raises
        --------
        TwitchHTTPException
            Bad request while fetching streams.
        """
        return await self._http._get_streams(self.name)


class User(Messageable):

    def __init__(self, **attrs):
        self._name = attrs.pop('author', None)
        self._writer = attrs.pop('_writer')
        self._channel = attrs.pop('channel', self._name)
        self._tags = attrs.pop('tags', None)

        if not self._tags:
            self._tags = {'None': 'None'}

        self.display_name = self._tags.get('display-name', self._name)
        self._id = int(self._tags.get('user-id', 0))
        self.type = self._tags.get('user-type', 'Empty')
        self._colour = self._tags.get('color', None)
        self.subscriber = self._tags.get('subscriber', None)
        self.turbo = self._tags.get('turbo', None)
        self._badges = self._tags.get('badges', ',').split(',')

    def __repr__(self):
        return '<User name={0.name} channel={0._channel}>'.format(self)

    async def _get_channel(self):
        return self.channel, self._name

    async def _get_writer(self):
        return self._writer

    async def _get_method(self):
        return self.__class__.__name__

    @property
    def name(self):
        """The users name."""
        return self._name

    @property
    def id(self):
        """The users ID.

         Could be None if no Tags were received."""
        return self._id

    @property
    def channel(self):
        """The channel object associated with the User.

        Notes
        -------
            The channel will be valid for the data which triggered the Event. But it's possible the
            user could be in multiple channels. E.g: The User BobRoss sends a message from the Channel ArtIsCool.
            The Channel object received will be ArtIsCool."""
        return self._channel

    @property
    def colour(self):
        """The users colour.

        Could be None if no Tags were received.
        """
        return self._colour

    @property
    def color(self):
        """An American-English alias to colour."""
        return self.colour

    @property
    def is_turbo(self):
        """A boolean indicating whether the User is Turbo.

        Could be None if no Tags were received.
        """
        return self.turbo

    @property
    def is_subscriber(self):
        """A boolean indicating whether the User is a subscriber of the current channel.

        Could be None if no Tags were received.
        """
        return self.subscriber

    @property
    def badges(self):
        """The badges associated with the User.

        Could be None if no Tags were received.
        """
        return self._badges

    @property
    def tags(self):
        """The Tags received for the User.

        Could be a Dict containing None if no tags were received.
        """
        return self._tags


class Context(Messageable):

    def __init__(self, message: Message, channel: Channel, user: User, **attrs):
        self.message = message
        self.channel = channel
        self.content = message.content
        self.author = user
        self.prefix = attrs.get('prefix', None)

        self._writer = self.channel._writer

        self.command = attrs.get('Command', None)
        self.args = attrs.get('args', None)
        self.kwargs = attrs.get('kwargs', None)

    async def _get_channel(self):
        return self.channel.name, None

    async def _get_writer(self):
        return self._writer

    async def _get_method(self):
        return self.__class__.__name__

    async def get_stream(self):
        """|coro|

        Method which retrieves stream information on the channel stored in Context; provided it is active(Live).

        Returns
        ---------
        dict
            Dict containing active streamer data. Could be None if the stream is not live.

        Raises
        --------
        TwitchHTTPException
            Bad request while fetching streams.
        """
        return await self.channel.get_stream()
