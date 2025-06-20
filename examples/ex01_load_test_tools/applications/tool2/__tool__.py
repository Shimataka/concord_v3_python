from discord.ext.commands import Cog, CommandError, Context, has_permissions, hybrid_command
from discord.ext.tasks import loop
from discord.message import Message

from concord import Agent


class TestTool2(Cog):
    """TestTool2

    Args:
        agent (Agent): BOTのコア部分となるAgentクラス。
    """

    def __init__(self, agent: Agent) -> None:
        self.agent = agent
        self.template_tool_task2.start()

    @loop(seconds=10, count=5)
    async def template_tool_task2(self) -> None:
        """template_tool_task2

        テンプレートツール (コピー用)

        """
        await self.agent.cached_channels.dev_channel.send(
            content=f"Task! {self.template_tool_task2.current_loop}",
        )

    @template_tool_task2.error
    async def template_tool_task2_error(self, error: BaseException) -> None:
        """template_tool_task2_error

        Run on any error is raised

        Args:
            error (BaseException): Catched error.

        Raises:
            error: Catched error recall
        """
        raise error

    @template_tool_task2.after_loop
    async def template_tool_task2_afterloop(self) -> None:
        """template_tool_task2_afterloop

        Run on all loops are finished.

        """
        await self.agent.cached_channels.dev_channel.send(
            content="END!",
        )

    @hybrid_command()  # type: ignore[arg-type]
    @has_permissions(administrator=True)
    async def template_tool_command2(
        self,
        context: Context,  # type: ignore[type-arg, reportUnknownReturnType]
    ) -> None:
        """テンプレート1コマンドの説明"""
        await context.send("Accept")

    @template_tool_command2.error  # type: ignore[reportUnknownReturnType]
    async def template2_error(
        self,
        context: Context,  # type: ignore[type-arg, reportUnknownReturnType]  # noqa: ARG002
        error: CommandError,  # type: ignore[type-arg, reportUnknownReturnType]
    ) -> None:
        raise error

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        """on_message

        メッセージ投稿イベントで応答(systemとbotの投稿は除く)

        Args:
            message (Message): discord.message.Message
        """
        if message.is_system():
            return
        if message.author.bot:
            return

        await message.reply(content=echo(message=message))


def echo(message: Message) -> str:
    """Echo

    Args:
        message (Message): discord.Message

    Returns:
        str: discord.Message.content
    """
    return message.content  # type: ignore[reportUnknownMemberType]
