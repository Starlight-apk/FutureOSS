
    def __init__(self):
        self.engine = I18nEngine()
        self.middleware_handler = None

    def meta(self):
        
        加载语言文件并初始化中间件
        config = {}
        if deps:
            config = deps.get("config", {})
        
        default_locale = config.get("default_locale", "zh-CN")
        fallback_locale = config.get("fallback_locale", "en-US")
        supported_locales = config.get("supported_locales", ["zh-CN", "en-US", "zh-TW"])
        locales_dir = config.get("locales_dir", "locales")
        
        plugin_dir = Path(__file__).parent
        full_locales_dir = plugin_dir / locales_dir
        
        self.engine.set_fallback(fallback_locale)
        
        self.engine.load_locales(str(full_locales_dir), supported_locales)
        
        self.engine.set_locale(default_locale)
        
        self.middleware_handler = I18nMiddleware(self.engine, config)
        
        Log.info("i18n", f"已加载语言: {', '.join(supported_locales)}")
        Log.info("i18n", f"默认语言: {default_locale}")

    def start(self):
        http_api = None
        if hasattr(self, 'set_http_api'):
            http_api = getattr(self, '_http_api', None)
        
        if http_api and hasattr(http_api, 'router'):
            http_api.router.get("/api/i18n/locales", self._locales_handler)
            http_api.router.get("/api/i18n/translate", self._translate_handler)
            http_api.router.post("/api/i18n/locale", self._change_locale_handler)
            Log.info("i18n", "API 路由已注册")

    def stop(self):
        return self.engine is not None

    def stats(self) -> dict:
        self._http_api = http_api


    def _locales_handler(self, request):
        
        GET /api/i18n/translate?key=user.greeting&locale=en-US&name=World
        from oss.plugin.types import Response
        t = getattr(request, 't', self.engine.t)
        
        query = request.path.split("?", 1)[-1] if "?" in request.path else ""
        params = {}
        for param in query.split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                params[key] = value
        
        key = params.get("key", "")
        locale = params.get("locale", None)
        
        if not key:
            return Response(
                status=400,
                body=json.dumps({"error": t("api.missing_param", param="key")}),
                headers={"Content-Type": "application/json"}
            )
        
        result = t(key, locale=locale, **params)
        
        return Response(
            status=200,
            body=json.dumps({
                "key": key,
                "locale": locale or self.engine.get_locale(),
                "text": result
            }),
            headers={"Content-Type": "application/json"}
        )

    def _change_locale_handler(self, request):
        from oss.plugin.types import Response
        t = getattr(request, 't', self.engine.t)
        
        try:
            body = json.loads(request.body) if hasattr(request, 'body') and request.body else {}
        except json.JSONDecodeError:
            body = {}
        
        new_locale = body.get("locale", "")
        
        if not new_locale:
            return Response(
                status=400,
                body=json.dumps({"error": t("api.missing_param", param="locale")}),
                headers={"Content-Type": "application/json"}
            )
        
        if not self.engine.is_valid_locale(new_locale):
            return Response(
                status=400,
                body=json.dumps({"error": t("plugin.locale_not_supported", locale=new_locale)}),
                headers={"Content-Type": "application/json"}
            )
        
        self.engine.set_locale(new_locale)
        
        return Response(
            status=200,
            body=json.dumps({"message": t("plugin.locale_changed", locale=new_locale)}),
            headers={"Content-Type": "application/json"}
        )


register_plugin_type("I18nPlugin", I18nPlugin)


def New():
    return I18nPlugin()
