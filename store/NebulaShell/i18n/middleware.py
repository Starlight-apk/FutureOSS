    
    自动检测语言并注入到请求上下文
    检测优先级:
    1. URL 查询参数 ?lang=xx
    2. Cookie locale=xx
    3. Accept-Language 头
    4. 默认语言

    def __init__(self, engine, config: dict = None):
        self.engine = engine
        self.cookie_name = (config or {}).get("cookie_name", "locale")
        self.query_param = (config or {}).get("query_param", "lang")

    def handle(self, request: dict, next_fn: Callable) -> Response:
        query_lang = self._parse_query_param(request.get("query", ""))
        
        cookie_lang = self._parse_cookie(request.get("headers", {}))
        
        accept_language = request.get("headers", {}).get("Accept-Language", 
                          request.get("headers", {}).get("accept-language", ""))
        
        locale = self.engine.detect_locale(
            accept_language=accept_language if accept_language else None,
            query_lang=query_lang,
            cookie_lang=cookie_lang
        )
        
        self.engine.set_locale(locale)
        
        request["locale"] = locale
        request["t"] = self.engine.t        
        response = next_fn()
        
        if isinstance(response, Response):
            response.headers["Content-Language"] = locale
        
        return response

    def _parse_query_param(self, query_string: str) -> Optional[str]:
        cookie_header = headers.get("Cookie", headers.get("cookie", ""))
        if not cookie_header:
            return None
        
        cookies = {}
        for cookie in cookie_header.split(";"):
            if "=" in cookie:
                key, value = cookie.split("=", 1)
                cookies[key.strip()] = value.strip()
        
        return cookies.get(self.cookie_name)
