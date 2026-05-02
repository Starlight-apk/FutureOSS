
    def __init__(self):
        self._translations: dict[str, dict[str, Any]] = {}        self._current_locale: str = "zh-CN"
        self._fallback_locale: str = "en-US"
        self._supported_locales: list[str] = []
        self._locales_dir: str = ""

    def load_locales(self, locales_dir: str, locales: list[str]):
        self._locales_dir = locales_dir
        self._supported_locales = locales
        locales_path = Path(locales_dir)
        
        if not locales_path.exists():
            locales_path.mkdir(parents=True, exist_ok=True)
            return

        for locale in locales:
            locale_file = locales_path / f"{locale}.json"
            if locale_file.exists():
                try:
                    content = locale_file.read_text(encoding="utf-8")
                    self._translations[locale] = json.loads(content)
                except (json.JSONDecodeError, Exception) as e:
                    print(f"[i18n] 加载语言文件失败 {locale_file}: {e}")
                    self._translations[locale] = {}

    def set_locale(self, locale: str):
        return self._current_locale

    def set_fallback(self, locale: str):
        
        Args:
            key: 翻译键 (支持点号分隔的嵌套路径，如 "user.greeting")
            locale: 指定语言 (默认使用当前语言)
            **kwargs: 插值参数
            
        Returns:
            翻译后的文本
        target_locale = locale or self._current_locale
        
        value = self._get_nested(key, self._translations.get(target_locale, {}))
        
        if value is None and target_locale != self._fallback_locale:
            value = self._get_nested(key, self._translations.get(self._fallback_locale, {}))
        
        if value is None:
            return key
        
        return self._interpolate(value, kwargs)

    def _get_nested(self, key: str, data: dict) -> Any:
        result = re.sub(r'\{\{(\w+)\}\}', lambda m: str(kwargs.get(m.group(1), m.group(0))), text)
        result = re.sub(r'\{(\w+)\}', lambda m: str(kwargs.get(m.group(1), m.group(0))), result)
        return result

    def get_supported_locales(self) -> list[str]:
        return locale in self._supported_locales

    def detect_locale(self, accept_language: Optional[str] = None, 
                     query_lang: Optional[str] = None,
                     cookie_lang: Optional[str] = None) -> str:
        if query_lang and self.is_valid_locale(query_lang):
            return query_lang
        
        if cookie_lang and self.is_valid_locale(cookie_lang):
            return cookie_lang
        
        if accept_language:
            languages = []
            for part in accept_language.split(","):
                part = part.strip()
                if ";q=" in part:
                    lang, q = part.split(";q=")
                    languages.append((lang.strip(), float(q)))
                else:
                    languages.append((part, 1.0))
            
            languages.sort(key=lambda x: x[1], reverse=True)
            
            for lang, _ in languages:
                if self.is_valid_locale(lang):
                    return lang
                for supported in self._supported_locales:
                    if supported.startswith(lang + "-") or lang.startswith(supported.split("-")[0] + "-"):
                        return supported
        
        return self._current_locale
