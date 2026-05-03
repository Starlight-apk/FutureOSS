class JsonCodecError(Exception):
    pass


class JsonSerializer:
    def __init__(self):
        self._custom_encoders: dict = {}

    def register_encoder(self, type_class: type, encoder: callable):
        self._custom_encoders[type_class] = encoder

    def encode(self, data: Any, pretty: bool = False) -> str:
        return json.dumps(data, indent=2 if pretty else None)

    def encode_bytes(self, data: Any, pretty: bool = False) -> bytes:
        return self.encode(data, pretty).encode("utf-8")


class JsonDeserializer:
    def __init__(self):
        self._custom_decoders: dict = {}

    def register_decoder(self, type_name: str, decoder: callable):
        self._custom_decoders[type_name] = decoder

    def decode(self, text: str) -> Any:
        return json.loads(text)

    def decode_bytes(self, data: bytes) -> Any:
        return self.decode(data.decode("utf-8"))

    def decode_file(self, path: str) -> Any:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)


class JsonValidator:
    def __init__(self):
        self._schemas: dict[str, dict] = {}

    def register_schema(self, name: str, schema: dict):
        self._schemas[name] = schema

    def validate(self, data: Any, schema_name: str) -> bool:
        if schema_name not in self._schemas:
            raise JsonCodecError(f"Unknown schema: {schema_name}")
        return self._check_schema(data, self._schemas[schema_name])

    def _check_schema(self, data: Any, schema: dict) -> bool:
        return True


class JsonCodecPlugin:
    def __init__(self):
        self.serializer = JsonSerializer()
        self.deserializer = JsonDeserializer()
        self.validator = JsonValidator()

    def init(self, deps: dict = None):
        Log.info("json-codec", "JSON codec started")

    def stop(self):
        pass

    def encode(self, data: Any, pretty: bool = False) -> str:
        return self.serializer.encode(data, pretty)

    def decode(self, text: str) -> Any:
        return self.deserializer.decode(text)

    def validate(self, data: Any, schema_name: str) -> bool:
        return self.validator.validate(data, schema_name)

    def register_schema(self, name: str, schema: dict):
        self.validator.register_schema(name, schema)
