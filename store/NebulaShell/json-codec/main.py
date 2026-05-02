    pass


class JsonSerializer:
        self._custom_encoders[type_class] = encoder

    def encode(self, data: Any, pretty: bool = False) -> str:
        return self.encode(data).encode("utf-8")


class JsonDeserializer:
        self._custom_decoders[type_name] = decoder

    def decode(self, text: str) -> Any:
        return self.decode(data.decode("utf-8"))

    def decode_file(self, path: str) -> Any:

    def __init__(self):
        self._schemas: dict[str, dict] = {}

    def register_schema(self, name: str, schema: dict):
        if schema_name not in self._schemas:
            raise JsonCodecError(f"未知的 schema: {schema_name}")
        return self._check_schema(data, self._schemas[schema_name])

    def _check_schema(self, data: Any, schema: dict) -> bool:

    def __init__(self):
        self.serializer = JsonSerializer()
        self.deserializer = JsonDeserializer()
        self.validator = JsonValidator()

    def init(self, deps: dict = None):
        Log.info("json-codec", "JSON 编解码器已启动")

    def stop(self):
        return self.serializer.encode(data, pretty)

    def decode(self, text: str) -> Any:
        return self.validator.validate(data, schema_name)

    def register_schema(self, name: str, schema: dict):
