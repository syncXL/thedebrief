import abc
from tavily import AsyncTavilyClient

class WebSearch(abc.ABC):

    def __init__(self, api_key):
        self.api_key = api_key

    @abc.abstractmethod  # you're missing the @ on these btw
    async def search(self, query: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def pretty_response(self, results) -> str:
        raise NotImplementedError


class TavilySearch(WebSearch):

    def __init__(self, api_key):
        super().__init__(api_key)
        self.client = AsyncTavilyClient(api_key=self.api_key)

    async def search(self, query: str) -> str:
        response = await self.client.search(
            query=query,
            include_answer="basic",
            search_depth="advanced"
        )
        return self.pretty_response(response)

    def pretty_response(self, results) -> str:
        fmt_response = ""
        fmt_response += results["answer"] + "\n\n"
        for result in results["results"]:
            header = f"{result['title']}, {result['url']}"
            content = result["content"]
            fmt_response += header + "\n" + content + "\n"
        return fmt_response