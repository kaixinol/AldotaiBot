# 模块移植自 https://github.com/Redlnn/redbot/blob/master/util/control/permission.py
from graia.ariadne.app import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.model import Group, Member, MemberPerm
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend

from util.initializer import ReadConfig


class PermConfig:
    __filename__: str = "permission"
    group_blacklist: list[int] = []
    user_blacklist: list[int] = []


perm_cfg = PermConfig()
perm_cfg.group_blacklist = ReadConfig("ignored group")
perm_cfg.group_blacklist = ReadConfig("abuser")
basic_cfg = ReadConfig("control")


class GroupPermission:
    """
    用于管理权限的类，不应被实例化
    适用于群消息和来自群的临时会话
    """

    BOT_MASTER: int = 100  # Bot主人
    BOT_ADMIN: int = 90  # Bot管理员
    OWNER: int = 30  # 群主
    ADMIN: int = 20  # 群管理员
    USER: int = 10  # 群成员/好友
    BANED: int = 0  # Bot黑名单成员
    DEFAULT: int = USER

    _levels = {
        MemberPerm.Member: USER,
        MemberPerm.Administrator: ADMIN,
        MemberPerm.Owner: OWNER,
    }

    @classmethod
    async def get(cls, target: Member) -> int:
        """
        获取用户的权限等级

        :param target: Friend 或 Member 实例
        :return: 等级，整数
        """
        if target.id == basic_cfg["master"]:
            return cls.BOT_MASTER
        elif target.id in basic_cfg["admins"]:
            return cls.BOT_ADMIN
        elif isinstance(target, Member):
            return cls._levels[target.permission]
        else:
            return cls.DEFAULT

    @classmethod
    def require(
        cls,
        perm: MemberPerm | int = MemberPerm.Member,
        send_alert: bool = True,
        alert_text: str = "你没有权限执行此指令",
    ) -> Depend:
        """
        群消息权限检查
        指示需要 `level` 以上等级才能触发
        :param perm: 至少需要什么权限才能调用
        :param send_alert: 是否发送无权限消息
        :param alert_text: 无权限提示的消息内容
        """

        async def wrapper(app: Ariadne, group: Group, member: Member):
            if (
                group.id in perm_cfg.group_blacklist
                or member.id in perm_cfg.user_blacklist
            ):
                raise ExecutionStop()
            if isinstance(perm, MemberPerm):
                target = cls._levels[perm]
            elif isinstance(perm, int):
                target = perm
            else:
                raise ValueError("perm 参数类型错误")
            if (await cls.get(member)) < target:
                if send_alert:
                    await app.send_message(
                        group, MessageChain(At(member.id), Plain(f" {alert_text}"))
                    )
                raise ExecutionStop()

        return Depend(wrapper)
