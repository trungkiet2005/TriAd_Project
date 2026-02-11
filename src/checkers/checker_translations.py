"""
Checker Translations
Contains prompt templates for checkers in supported languages, 
handling both Payoff (maximization) and Penalty (minimization) contexts.
"""

TRANSLATIONS = {
    "en": {
        "unit_points": "point",
        "unit_penalty": "penalty",
        "join_and": " and ",
        "join_comma": ", ",
        
        # Game Rules / Context
        "context_intro": "{players} are playing a multi-round game.",
        "context_action": "At each turn {players} simultaneously perform one of the following actions: {actions}",
        "context_payoff_intro": "The {unit}s for each combination of chosen actions are the following:",
        "context_rounds": "They will play a total of {n_rounds} rounds of this game.",
        "context_objective_max": "Remember that a player's objective is to get the highest possible amount of {unit}s in the long run.",
        "context_objective_min": "Remember that a player's objective is to minimize their {unit} in the long run.",
        
        "payoff_description_points": "player {player} collects {value} {unit}s",
        "payoff_description_penalty": "player {player} gets a {unit} of {value}",
        
        "history_intro": "The history of the game in the last {window} rounds is the following:",
        "history_round": "Round {round}: {actions_desc}. {scores_desc}.",
        "history_action": "player {player} played \"{action}\"",
        "history_score_points": "player {player} got {value} {unit}s",
        "history_score_penalty": "player {player} got a {unit} of {value}",
        "history_current_round": "Current round: {round}.",
        "history_ended": "The game has ended.",
        
        # Rule Checker
        "rule_max_val": "What is the highest {unit} player {player} can get in a single round?",
        "rule_min_val": "What is the lowest {unit} player {player} can get in a single round?",
        "rule_allowed_actions": "Which actions is player {player} allowed to play?",
        "rule_combo_payoff": "What is player {player}'s {unit} in a single round if {conditions}?",
        "condition_play": "player {player} plays '{action}'",
        
        # Aggregation Checker
        "agg_action_count": "How many times did player {player} choose {action}?",
        "agg_total_score": "What is player {player}'s current total {unit}?",
        
        # Time Checker
        "time_current_round": "Which is the current round of the game?",
        "time_action_round": "Which action did player {player} play in round {round}?",
        "time_score_round": "How many {unit}s did player {player} collect in round {round}?",
    },
    "vn": {
        "unit_points": "điểm",
        "unit_penalty": "hình phạt",
        "join_and": " và ",
        "join_comma": ", ",
        
        # Game Rules / Context
        "context_intro": "{players} đang chơi một trò chơi gồm nhiều vòng.",
        "context_action": "Ở mỗi lượt, {players} đồng thời thực hiện một trong các hành động sau: {actions}",
        "context_payoff_intro": "Các {unit} cho từng kết hợp hành động được tính như sau:",
        "context_rounds": "Họ sẽ chơi tổng cộng {n_rounds} vòng.",
        "context_objective_max": "Hãy nhớ rằng mục tiêu của người chơi là đạt được số {unit} cao nhất có thể trong dài hạn.",
        "context_objective_min": "Hãy nhớ rằng mục tiêu của người chơi là giảm thiểu {unit} của họ trong dài hạn.",
        
        "payoff_description_points": "người chơi {player} nhận được {value} {unit}",
        "payoff_description_penalty": "người chơi {player} chịu một {unit} là {value}",
        
        "history_intro": "Lịch sử trò chơi trong {window} vòng gần nhất như sau:",
        "history_round": "Vòng {round}: {actions_desc}. {scores_desc}.",
        "history_action": "người chơi {player} đã chọn \"{action}\"",
        "history_score_points": "người chơi {player} được {value} {unit}",
        "history_score_penalty": "người chơi {player} chịu {unit} {value}",
        "history_current_round": "Vòng hiện tại: {round}.",
        "history_ended": "Trò chơi đã kết thúc.",
        
        # Rule Checker
        "rule_max_val": "Mức {unit} cao nhất mà người chơi {player} có thể nhận trong một vòng là bao nhiêu?",
        "rule_min_val": "Mức {unit} thấp nhất mà người chơi {player} có thể nhận trong một vòng là bao nhiêu?",
        "rule_allowed_actions": "Người chơi {player} được phép thực hiện những hành động nào?",
        "rule_combo_payoff": "{unit} của người chơi {player} trong một vòng là bao nhiêu nếu {conditions}?",
        "condition_play": "người chơi {player} chọn '{action}'",
        
        # Aggregation Checker
        "agg_action_count": "Người chơi {player} đã chọn {action} bao nhiêu lần?",
        "agg_total_score": "Tổng {unit} hiện tại của người chơi {player} là bao nhiêu?",
        
        # Time Checker
        "time_current_round": "Hiện tại đang là vòng thứ mấy của trò chơi?",
        "time_action_round": "Người chơi {player} đã chọn hành động nào trong vòng {round}?",
        "time_score_round": "Người chơi {player} đã nhận bao nhiêu {unit} trong vòng {round}?",
    },

    "fr": {
        "unit_points": "point",
        "unit_penalty": "pénalité",
        "join_and": " et ",
        "join_comma": ", ",
        
        # Game Rules / Context
        "context_intro": "{players} jouent à un jeu à plusieurs tours.",
        "context_action": "À chaque tour, {players} effectuent simultanément l'une des actions suivantes : {actions}",
        "context_payoff_intro": "Les {unit}s pour chaque combinaison d'actions choisies sont les suivantes :",
        "context_rounds": "Ils joueront au total {n_rounds} tours de ce jeu.",
        "context_objective_max": "N'oubliez pas que l'objectif d'un joueur est d'obtenir le montant le plus élevé possible de {unit}s à long terme.",
        "context_objective_min": "N'oubliez pas que l'objectif d'un joueur est de minimiser sa {unit} à long terme.",
        
        "payoff_description_points": "le joueur {player} reçoit {value} {unit}s",
        "payoff_description_penalty": "le joueur {player} reçoit une {unit} de {value}",
        
        "history_intro": "L'historique du jeu au cours des {window} derniers tours est le suivant :",
        "history_round": "Tour {round} : {actions_desc}. {scores_desc}.",
        "history_action": "le joueur {player} a joué \"{action}\"",
        "history_score_points": "le joueur {player} a obtenu {value} {unit}s",
        "history_score_penalty": "le joueur {player} a subi une {unit} de {value}",
        "history_current_round": "Tour actuel : {round}.",
        "history_ended": "Le jeu est terminé.",
        
        # Rule Checker
        "rule_max_val": "Quelle est la plus haute {unit} que le joueur {player} peut obtenir en un seul tour ?",
        "rule_min_val": "Quelle est la plus basse {unit} que le joueur {player} peut obtenir en un seul tour ?",
        "rule_allowed_actions": "Quelles actions le joueur {player} est-il autorisé à jouer ?",
        "rule_combo_payoff": "Quelle est la {unit} du joueur {player} en un seul tour si {conditions} ?",
        "condition_play": "le joueur {player} joue '{action}'",
        
        # Aggregation Checker
        "agg_action_count": "Combien de fois le joueur {player} a-t-il choisi {action} ?",
        "agg_total_score": "Quel est le total actuel de {unit} du joueur {player} ?",
        
        # Time Checker
        "time_current_round": "Quel est le tour actuel du jeu ?",
        "time_action_round": "Quelle action le joueur {player} a-t-il joué au tour {round} ?",
        "time_score_round": "Combien de {unit}s le joueur {player} a-t-il collecté au tour {round} ?",
    },
    "cn": {
        "unit_points": "分",
        "unit_penalty": "惩罚",
        "join_and": " 和 ",
        "join_comma": "，",
        
        # Game Rules / Context
        "context_intro": "{players} 正在进行多轮游戏。",
        "context_action": "在每一轮中，{players} 同时执行以下操作之一：{actions}",
        "context_payoff_intro": "每种操作组合的 {unit} 如下：",
        "context_rounds": "他们将总共进行 {n_rounds} 轮游戏。",
        "context_objective_max": "请记住，玩家的目标是长期获得尽可能高的 {unit}。",
        "context_objective_min": "请记住，玩家的目标是长期尽可能减少他们的 {unit}。",
        
        "payoff_description_points": "玩家 {player} 获得 {value} {unit}",
        "payoff_description_penalty": "玩家 {player} 受到 {value} 的 {unit}",
        
        "history_intro": "过去 {window} 轮的游戏记录如下：",
        "history_round": "第 {round} 轮：{actions_desc}。{scores_desc}。",
        "history_action": "玩家 {player} 选择了 \"{action}\"",
        "history_score_points": "玩家 {player} 获得了 {value} {unit}",
        "history_score_penalty": "玩家 {player} 受到了 {value} 的 {unit}",
        "history_current_round": "当前轮次：{round}。",
        "history_ended": "游戏结束。",
        
        # Rule Checker
        "rule_max_val": "玩家 {player} 在单轮中能获得的最高 {unit} 是多少？",
        "rule_min_val": "玩家 {player} 在单轮中能获得的最低 {unit} 是多少？",
        "rule_allowed_actions": "玩家 {player} 允许执行哪些操作？",
        "rule_combo_payoff": "如果 {conditions}，玩家 {player} 在单轮中的 {unit} 是多少？",
        "condition_play": "玩家 {player} 选择 '{action}'",
        
        # Aggregation Checker
        "agg_action_count": "玩家 {player} 选择了 {action} 多少次？",
        "agg_total_score": "玩家 {player} 当前的总 {unit} 是多少？",
        
        # Time Checker
        "time_current_round": "当前是游戏的第几轮？",
        "time_action_round": "玩家 {player} 在第 {round} 轮选择了什么操作？",
        "time_score_round": "玩家 {player} 在第 {round} 轮获得了多少 {unit}？",
    },
    "ar": {
        "unit_points": "نقاط",
        "unit_penalty": "عقوبة",
        "join_and": " و ",
        "join_comma": "، ",
        
        "context_intro": "{players} يلعبون لعبة متعددة الجولات.",
        "context_action": "في كل دور يقوم {players} في وقت واحد بتنفيذ أحد الإجراءات التالية: {actions}",
        "context_payoff_intro": "الـ {unit} لكل مجموعة من الإجراءات المختارة هي كما يلي:",
        "context_rounds": "سيلعبون ما مجموعه {n_rounds} جولات من هذه اللعبة.",
        "context_objective_max": "تذكر أن هدف اللاعب هو الحصول على أعلى قدر ممكن من {unit} على المدى الطويل.",
        "context_objective_min": "تذكر أن هدف اللاعب هو تقليل {unit} الخاصة بهم على المدى الطويل.",
        
        "payoff_description_points": "اللاعب {player} يجمع {value} {unit}",
        "payoff_description_penalty": "اللاعب {player} يحصل على {unit} قدرها {value}",
        
        "history_intro": "تاريخ اللعبة في آخر {window} جولات كما يلي:",
        "history_round": "الجولة {round}: {actions_desc}. {scores_desc}.",
        "history_action": "اللاعب {player} لعب \"{action}\"",
        "history_score_points": "اللاعب {player} حصل على {value} {unit}",
        "history_score_penalty": "اللاعب {player} حصل على {unit} قدرها {value}",
        "history_current_round": "الجولة الحالية: {round}.",
        "history_ended": "انتهت اللعبة.",
        
        "rule_max_val": "ما هي أعلى {unit} يمكن أن يحصل عليها اللاعب {player} في جولة واحدة؟",
        "rule_min_val": "ما هي أقل {unit} يمكن أن يحصل عليها اللاعب {player} في جولة واحدة؟",
        "rule_allowed_actions": "ما هي الإجراءات المسموح للاعب {player} بلعبها؟",
        "rule_combo_payoff": "ما هي {unit} اللاعب {player} في جولة واحدة إذا {conditions}؟",
        "condition_play": "اللاعب {player} يلعب '{action}'",
        
        "agg_action_count": "كم مرة اختار اللاعب {player} الإجراء {action}؟",
        "agg_total_score": "ما هو إجمالي {unit} الحالي للاعب {player}؟",
        
        "time_current_round": "ما هي الجولة الحالية من اللعبة؟",
        "time_action_round": "أي إجراء لعبه اللاعب {player} في الجولة {round}؟",
        "time_score_round": "كم عدد {unit} التي جمعها اللاعب {player} في الجولة {round}؟",
    },
    "it": {
        "unit_points": "punti",
        "unit_penalty": "penalità",
        "join_and": " e ",
        "join_comma": ", ",
        
        "context_intro": "{players} stanno giocando a un gioco a più turni.",
        "context_action": "A ogni turno {players} eseguono simultaneamente una delle seguenti azioni: {actions}",
        "context_payoff_intro": "I {unit} per ogni combinazione di azioni scelte sono i seguenti:",
        "context_rounds": "Giocheranno un totale di {n_rounds} turni di questo gioco.",
        "context_objective_max": "Ricorda che l'obiettivo di un giocatore è ottenere la maggior quantità possibile di {unit} a lungo termine.",
        "context_objective_min": "Ricorda che l'obiettivo di un giocatore è minimizzare la propria {unit} a lungo termine.",
        
        "payoff_description_points": "il giocatore {player} raccoglie {value} {unit}",
        "payoff_description_penalty": "il giocatore {player} ottiene una {unit} di {value}",
        
        "history_intro": "La cronologia del gioco negli ultimi {window} turni è la seguente:",
        "history_round": "Turno {round}: {actions_desc}. {scores_desc}.",
        "history_action": "il giocatore {player} ha giocato \"{action}\"",
        "history_score_points": "il giocatore {player} ha ottenuto {value} {unit}",
        "history_score_penalty": "il giocatore {player} ha subito una {unit} di {value}",
        "history_current_round": "Turno attuale: {round}.",
        "history_ended": "Il gioco è finito.",
        
        "rule_max_val": "Qual è il {unit} più alto che il giocatore {player} può ottenere in un singolo turno?",
        "rule_min_val": "Qual è il {unit} più basso che il giocatore {player} può ottenere in un singolo turno?",
        "rule_allowed_actions": "Quali azioni è autorizzato a giocare il giocatore {player}?",
        "rule_combo_payoff": "Qual è il {unit} del giocatore {player} in un singolo turno se {conditions}?",
        "condition_play": "il giocatore {player} gioca '{action}'",
        
        "agg_action_count": "Quante volte il giocatore {player} ha scelto {action}?",
        "agg_total_score": "Qual è il totale attuale di {unit} del giocatore {player}?",
        
        "time_current_round": "Qual è il turno attuale del gioco?",
        "time_action_round": "Quale azione ha giocato il giocatore {player} nel turno {round}?",
        "time_score_round": "Quanti {unit} ha raccolto il giocatore {player} nel turno {round}?",
    }
}

def get_translation(lang: str, key: str, **kwargs) -> str:
    """
    Get translated string and format it.
    Fallback to 'en' if lang is not found.
    """
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    template = lang_dict.get(key, TRANSLATIONS["en"].get(key, f"MISSING_{key}"))
    try:
        return template.format(**kwargs)
    except KeyError as e:
        return template # Return raw if formatting fails
