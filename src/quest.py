from enum import Enum, auto


class QuestStage(Enum):
    NOT_ACCEPTED = auto()
    ACCEPTED = auto()
    CLEARED = auto()
    RETURNED = auto()
    COMPLETE = auto()


class QuestManager:
    """西游记观音院主线任务状态机。

    流程：土地公给任务 -> 进入观音院 -> 击败妖怪 -> 返回村庄复命 -> 结局。
    剧情推进集中在此处，Game 只负责在合适时机调用并查询状态，
    避免剧情逻辑散落在交互代码里。
    """

    DIALOGS = {
        "god": {
            QuestStage.NOT_ACCEPTED: "大圣，观音院近日妖气缠身，恳请您前去降妖除魔！",
            QuestStage.ACCEPTED: "观音院就在前方，万望大圣多加小心。",
            QuestStage.CLEARED: "观音院就在前方，万望大圣多加小心。",
            QuestStage.RETURNED: "大圣可是降妖归来？快与老朽说说经过。",
            QuestStage.COMPLETE: "妖患已除，观音院重归安宁，多谢大圣！",
        },
        "guard": {
            QuestStage.NOT_ACCEPTED: "这林子最近不安宁，妖怪的巡逻队经常出没。你若要过路，先去村里找土地公打听清楚吧。",
            QuestStage.ACCEPTED: "哦？大圣接了土地公的差事？好！沿这条小路一直往东走就能到观音院。路上的妖怪交给你，林子我来守。",
            QuestStage.CLEARED: "大圣果然名不虚传！那黑熊精一除，我和弟兄们终于能安心巡山了。",
            QuestStage.RETURNED: "大圣回村复命去吧，土地公正等着你呢。",
            QuestStage.COMPLETE: "自大圣降妖之后，林子里太平多了，连野兔都多了几只！",
        },
        "apprentice": {
            QuestStage.NOT_ACCEPTED: "我跟着师父学采药呢...不过妖怪占了观音院，好多种药草都在寺院后山，唉。",
            QuestStage.ACCEPTED: "大圣要去观音院？那能不能...顺便帮我采一味灵芝回来？就在寺院后山的老松树下。",
            QuestStage.CLEARED: "大圣回来了！灵芝的事不急，您能平安归来就好。",
            QuestStage.RETURNED: "下次大圣路过，记得帮我看看那株灵芝还在不在呀。",
            QuestStage.COMPLETE: "师父说，大圣降妖除魔，是真正的活菩萨！",
        },
        "herbalist": {
            QuestStage.NOT_ACCEPTED: "我是这山里的采药人。最近妖怪出没，好些药草都采不到了。大圣若要去观音院，可得做好万全准备。",
            QuestStage.ACCEPTED: "我这有些金疮药，您拿着路上用。妖怪虽凶，但这山里的草药对付伤口最灵验不过了。",
            QuestStage.CLEARED: "大圣！您没受伤吧？快让我瞧瞧...哎呀齐天大圣果然了得，毫发无伤！",
            QuestStage.RETURNED: "大圣慢走，以后路过这儿，记得来坐坐。",
            QuestStage.COMPLETE: "自从妖怪没了，药草也多了起来。大圣是这山林的恩人！",
        },
        "merchant": {
            QuestStage.NOT_ACCEPTED: "唉，自从那黑熊精占了观音院，我这货都运不出去了。大圣你若能除了那妖怪，我沈某必有重谢！",
            QuestStage.ACCEPTED: "大圣要去降妖？好！我这儿有一壶上好的雄黄酒，您带着路上壮壮胆——不对，您不需要壮胆，就当解渴吧！",
            QuestStage.CLEARED: "痛快！那黑熊精也有今天！大圣，我沈某说话算话，今晚村里摆酒，请全村人给您庆功！",
            QuestStage.RETURNED: "酒席已经备好了，就等大圣回村啦！",
            QuestStage.COMPLETE: "大圣，酒席办了三天三夜，乡亲们都说您是观音院的大恩人！",
        },
    }

    def __init__(self):
        self.stage = QuestStage.NOT_ACCEPTED

    def accept(self):
        if self.stage == QuestStage.NOT_ACCEPTED:
            self.stage = QuestStage.ACCEPTED

    def clear_monsters(self):
        if self.stage == QuestStage.ACCEPTED:
            self.stage = QuestStage.CLEARED

    def mark_returned(self):
        if self.stage == QuestStage.CLEARED:
            self.stage = QuestStage.RETURNED

    def complete(self):
        if self.stage == QuestStage.RETURNED:
            self.stage = QuestStage.COMPLETE

    @property
    def can_enter_temple(self):
        return self.stage in (QuestStage.ACCEPTED, QuestStage.CLEARED)

    @property
    def should_return_to_village(self):
        return self.stage == QuestStage.CLEARED

    @property
    def is_complete(self):
        return self.stage == QuestStage.COMPLETE

    def dialog_for(self, layer_name):
        """返回当前阶段下该 NPC 的台词，没有阶段台词时返回 None（由调用方回退到默认台词）。"""
        stage_dialogs = self.DIALOGS.get(layer_name)
        if not stage_dialogs:
            return None
        return stage_dialogs.get(self.stage)
