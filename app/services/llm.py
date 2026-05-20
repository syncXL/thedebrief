import abc
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openrouter import ChatOpenRouter
from app.services.retry import llm_retry
from openrouter.errors import PaymentRequiredResponseError

logger = logging.getLogger(__name__)

class ModelProvider(abc.ABC):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    @abc.abstractmethod
    async def ainvoke(self, messages: list, tools=None, schema=None):
        raise NotImplementedError


class LangchainGoogle(ModelProvider):

    def __init__(self, api_key: str, model_name: str, use_or=False, google_api_key: str | None = None):
        super().__init__(api_key, model_name)
        self._google_api_key = google_api_key
        if not use_or:
            self._llm = ChatGoogleGenerativeAI(model=model_name, api_key=api_key)
        else:
            self._llm = ChatOpenRouter(model="google/" + model_name, api_key=api_key, max_retries=3)

    @llm_retry
    async def ainvoke(self, messages: list, tools=None, schema=None):
        try:
            return await self._call_llm(self._llm, messages, tools, schema)
        except PaymentRequiredResponseError:
            if not self._google_api_key:
                raise
            logger.warning(
                "OpenRouter payment required for %s, falling back to direct Google API",
                self.model_name,
            )
            fallback = ChatGoogleGenerativeAI(model=self.model_name, api_key=self._google_api_key)
            return await self._call_llm(fallback, messages, tools, schema)

    async def _call_llm(self, llm, messages: list, tools=None, schema=None):
        if tools:
            llm = llm.bind_tools(tools)
        if schema:
            llm = llm.with_structured_output(schema)
        return await llm.ainvoke(messages)
    

