bạn có thể tham khảo nè coi cách người ta viết bài nè ko cần quá nhiều phân tích số liệu : 
FAIRGAME: a Framework for AI Agents Bias
Recognition using Game Theory
Alessio Buscemia,*
,1, Daniele Proverbiob,1, Alessandro Di Stefanoc
, The Anh Hanc
, German Castignania and
Pietro Liòd
aLuxembourg Institute of Science and Technology
bDepartment of Industrial Engineering, University of Trento
cSchool Computing, Engineering and Digital Technologies, Teesside University
dDepartment of Computer Science and Technology, University of Cambridge
ORCID (Alessio Buscemi): https://orcid.org/0009-0003-4668-9915, ORCID (Daniele Proverbio):
https://orcid.org/0000-0002-0122-479X, ORCID (Alessandro Di Stefano): https://orcid.org/0000-0003-4905-3309,
ORCID (The Anh Han): https://orcid.org/0000-0002-3095-7714, ORCID (German Castignani):
https://orcid.org/0000-0001-5594-4904, ORCID (Pietro Liò): https://orcid.org/0000-0002-0540-5053
Abstract. Letting AI agents interact in multi-agent applications
adds a layer of complexity to the interpretability and prediction of
AI outcomes, with profound implications for their trustworthy adoption in research and society. Game theory offers powerful models
to capture and interpret strategic interaction among agents, but requires the support of reproducible, standardized and user-friendly
IT frameworks to enable comparison and interpretation of results.
To this end, we present FAIRGAME, a Framework for AI Agents
Bias Recognition using Game Theory. We describe its implementation and usage, and we employ it to uncover biased outcomes in
popular games among AI agents, depending on the employed Large
Language Model (LLM) and used language, as well as on the personality trait or strategic knowledge of the agents. Overall, FAIRGAME
allows users to reliably and easily simulate their desired games and
scenarios and compare the results across simulation campaigns and
with game-theoretic predictions, enabling the systematic discovery
of biases, the anticipation of emerging behavior out of strategic interplays, and empowering further research into strategic decisionmaking using LLM agents.
1 Introduction
AI agents powered by Large Language Models (LLM) are increasingly used in research [36], social [52] and industrial applications
[44, 50], calling for the development of accurate prediction frameworks for their behaviors during interactions among themselves or
with humans. Reliable predictions are essential for developing novel
applications, promoting trustworthy AI systems, and mitigating undesirable outcomes and biases [11, 23]. Numerous approaches have
been developed to improve the transparency and interpretability of
individual AI agents [5, 19], as well as to identify their inconsistencies, biases and hallucinations [12, 33, 34]. However, less is known
about cases where multiple interacting agents are involved [25],
where emerging biases may skew strategic outputs in unpredictable
∗ Corresponding Author. Email: alessio.buscemi@list.lu
1 Equal contribution.
manners. Studies emulating human behaviors [43] may produce spurious predictions. Also, in industry applications such as automated
dispute resolution [10, 20], auction design or pricing mechanisms
in finance and economics [8, 16, 17], or supply chain negotiations
[3, 38, 46], hidden biases may result in unjust decisions, disproportionate favoring of certain groups, and distortion of fair competition.
To address multi-agent interactions, and in addition to methods
tailored to individual agents, game theory [42] formalizes interactions as games, so as to model, predict and optimize the strategic
responses of rational agents [9, 20, 26]. Game theory has been employed to model and understand human choices in various contexts
[49, 51], and AI-based players have been increasingly tested to reproduce classical game scenarios and provide additional complexity to
them [22, 55, 56], as well as to interact in game-like distributed technologies [28]. However, due to varying research protocols and discipline constraints, bridging the gap between theoretical game theory
and empirical investigations of LLM agents in a reproducible, systematic and user-friendly setting is still a challenge [37].
To facilitate seamless and reproducible integration of gametheoretic evaluations of AI interactions, we introduce FAIRGAME
(Framework for AI Agents Bias Recognition using Game Theory), a
versatile framework designed to simulate diverse scenarios, ranging
from classical game theory models to realistic industrial use cases.
FAIRGAME is an open-source project [1].
In FAIRGAME, AI agents can be equipped with distinct features,
such as strategic attitudes and personalities, linguistic variations, cultural orientations and more. The framework allows quantitative simulations of arbitrarily complex games in a systematic and reproducible manner, and to observe the emerging outcomes brought about
by strategic interactions [27, 13], enabling direct comparison with
game-theoretic predictions and supporting the inference of strategies through observations of multiple experiments [39]. Incorporating AI agents into controlled and predictable scenarios will also help
identify and mitigate hidden biases related to language, cultural attributes, and more, which could result in suboptimal outcomes, unjust
advantages, ethical dilemmas, or systemic inefficiencies [15, 21, 24].
arXiv:2504.14325v4 [cs.AI] 31 Jan 2026
In this paper, we present the implementation of FAIRGAME, and
evaluate its usage and outputs across multiple games, human languages, and LLMs. Through several use cases, we show that our
empirical results recognize LLM biases in strategic interactions and
identify previously unknown inconsistencies across the LLMs used
to develop the agents. Overall, our results suggest that AI agents may
exhibit suboptimal behaviors when interacting through different languages and game contexts, and may deviate even significantly from
game-theoretic predictions. This supports the use of reproducible and
controlled simulation pipelines to predict the interacting behavior of
LLM agents, which defy classical modeling approaches. Finally, we
propose a scoring system to evaluate and compare the sensitivity of
LLMs to game determinants and strategies, so as to guide the selection of LLMs for the development of game-theoretic experiments and
strategic AI applications.
In the following, we first provide a comprehensive overview of
FAIRGAME, detailing its implementation and operational usage.
Then, we present our use cases: two common games in different variants and languages, with agents instantiated on different LLMs and
equipped with varying personalities and degrees of knowledge about
the game progression. Finally, we present our experimental findings
and scoring system, showing FAIRGAME’s efficacy in detecting biases and inconsistencies in AI-game-theoretic analyses.
2 Methodology: introducing FAIRGAME
FAIRGAME is a computational framework interfacing user-defined
instructions to create the desired agents, eventually delivering standardized outputs for subsequent processing (Fig. 1). It allows to test
user-defined games, described textually via prompt injection and including any desired payoff matrix, as well as to define traits of the
agents. The agents can be built from any LLM of choice, by calling the corresponding APIs (several of which are already provided
in our package; however, any usage fees are covered by the end
user). FAIRGAME requires the following inputs. First, a Configuration File: a JSON file that defines the setup of both the agents
and the game, in terms of parameters, payoff matrix entries, and additional information for the agents. For instance, agents can be associated with certain personalities, so as to increase the complexity
of human behavior emulators [29, 41] and predict the responses of
personality-driven autonomous agents [32, 40]. Table 1 provides a
detailed overview of the fields of the configuration file, along with
their explanation. An example of configuration file is in Supplementary Material Section S1 [2]. APrompt Template: a text file that
defines the instruction template, providing a literal description of the
game. It includes the instructions for each agent, with each round’s
parameters filled in from the configuration file, allowing customization of each agent. At runtime, this template is transformed into a
prompt that includes details on available strategies, the corresponding payoffs based on decisions, and other configuration-specified factors – such as an agent’s personality and awareness of the opponent’s
personality – as well as prior history information in case of repeated
games. This file can be translated in any language of choice, allowing
for multilingual tests. An example of an English prompt template for
a Prisoner’s Dilemma game is provided in Supplementary Material
Section S2 [2]. More than one prompt template can be associated to
the same config file.
Figure 1. Schematic representation of FAIRGAME flow of document
dependencies and outputs.
2.1 Creation and execution of games
Algorithm 1 processes the configuration file CF and the set of prompt
templates P T as inputs, and outputs a list G containing all instantiated games. The process involves validating inputs, extracting relevant game information, configuring agents, and creating the games.
First, the configuration file CF is validated to ensure that it conforms to the required structure and contains all necessary information (step 1). Similarly, the prompt templates PT are validated
against CF to confirm compatibility and completeness (step 2). After that, key information regarding the game to create is extracted
from the configuration file, including the list of languages (langs)
and the LLM (llm) and whether to compute all agent configuration permutations (all_agent_perm) (steps 3). If true, the function all_agent_perm generates all possible agent configurations of
the personalities and probabilities of knowing the opponent personality. Otherwise, pre-defined agent configurations are retrieved using
the get_agents_config function (step 4-8). An empty list G is then
initialized to store the created games (step 9). The algorithm iterates through each agent configuration (agent_config) to create the
games. For each configuration, agents are instantiated using the create_agents function, which sets up agents according to their configurations and the selected language model llm (step 10). A game instance is then created using create_game, which takes the information about the game, the agent details, and prompt templates as inputs
(step 11). The created game is appended to the list G (step 12). At
the end of the process, G contains all the instantiated games, each
configured with the appropriate agents, game parameters, and rules,
in suitable format for the LLMs.
Once instantiated, games are executed as per Algorithm 2. An
empty list O is initialized (step 1), which will be populated with
the outcomes of all games after execution. The list G is then given
as input to the algorithm. Each game g in G is processed independently (steps 2–9). If the user requests multiple rounds in an evolutionary game theory setting, a while loop governs their execution.
The loop continues as long as two conditions are satisfied: the current round count does not exceed the maximum number of rounds
Algorithm 1 Creation of games
Require: CF : Configuration file, P T: Prompt templates
Ensure: G: list of all instantiated games
1: validate_config_file(CF )
2: validate_templates(P T, CF )
3: game_info, langs, llm, all_agent_perm ← extract_info(CF )
4: if all_agent_perm then
5: agents_config ← compute_agents_combos(CF , langs)
6: else
7: agents_config ← get_agents_config(CF , langs)
8: end if
9: G ← ()
10: for ac in agents_config do
11: agents ← create_agents(ac, llm)
12: game ← create_games(game_info, agents, P T)
13: G.append(game)
14: end for
Table 1. Game Configuration Fields and Their Explanations
Field Subfield Type Explanation
name String Represents the name of the game or scenario being simulated.
nRounds Integer Specifies the maximum number of rounds to be played in the game.
nRoundsIsKnown Boolean Indicates whether the agents know the maximum number of rounds (True if known, False
otherwise).
llm String Defines which LLM will be used to simulate the agents.
languages List Lists the human languages in which the agents can be queried.
allAgentPermutations Boolean Specifies whether to compute all permutations of agent configurations or create only one
instance of the agents based on provided configurations.
agents Dictionary Contains configurations of the agents.
names List of Integers Identifiers or names of the agents.
personalities Dictionary Defines agents’ personalities, translated for each language. If a personality is ’None’, it
means that this information will be omitted from the prompt.
opponentPersonalityProb List of Integers Probability that a certain agent has a certain personality, as referred to the other agents. If
the probability is 0, this information is omitted from the prompt.
payoffMatrix Dictionary Contains information about the game’s payoff matrix.
weights Dictionary Specifies the weight values used in the payoff matrix.
strategies Dictionary Details strategies agents can adopt, translated for each language in languages.
combinations Dictionary Enumerates the possible combinations of strategies that both agents choose in each round.
matrix Dictionary Maps each combination to weights (payoffs) that agents receive when such scenarios
occur.
stopGameWhen List of Strings Specifies combinations in the payoff matrix that trigger the end of the game during a
round.
agentsCommunicate Boolean If True, the agents exchange a message with each other at each round before making a
decision; if False, they do not communicate.
Algorithm 2 Execution of games
Require: G: list of all instantiated games
Ensure: O: list of outcomes of all games
1: O ← ()
2: for g in G do
3: round ← 1
4: while round ≤ g.n_rounds and not_met(g.stop_cond) do
5: g.run_round()
6: round++
7: end while
8: O.append(g.history())
9: end for
g.n_rounds, and the game-specific stopping condition g.stop_cond
is not met (step 4). The stopping condition allows for the game to
terminate early based on predefined criteria, ensuring flexibility in
simulation. Within each iteration of the while loop, the function
g.run_round() is called to execute the logic for the current round
(step 5). This function, which is described in detail in Algorithm 3,
simulates the actions of the agents involved in the game. Note that
communication between agents is supported by FAIRGAME; however, we do not use it in the next use cases, hence the algorithm described here represents a simplified version that does not take interagent communication into account. We have dedicated a separate
study to analyzing the effect of communication by comparing outcomes with and without it [14].
Once the game terminates -— either because the maximum number of rounds has been reached or the stopping condition is satisfied
-— the algorithm retrieves the game’s history, which is appended to
the output file O (step 8).
Algorithm 3 describes how actions are simulated. For each agent,
the algorithm first retrieves its opponent agent – or agents, in case
of more than two players (step 2). It then determines the appropriate
template language for the agent, which is based on its language preference (step 3). Using this template language, a prompt is created
that incorporates key elements of the game’s current state, such as
the total number of rounds, the current round, whether the number of
rounds is known, the payoff matrix, and the game’s history (step 4).
Next, the agent chooses a strategy for the current round based on the
generated prompt (step 5). The corresponding payoff for this strategy
is then computed (step 6), and the game’s history is updated with the
agent’s move and resulting payoff (step 7). After both agents completed their actions, FAIRGAME proceeds to the next round, and the
process continues until all rounds are executed, as per Algorithm 2.
Algorithm 3 Run round
Require: g: game
Ensure: The history of the game is updated
1: for agent in agents do
2: opponents ← get_opponents(agents)
3: template_lang ← get_template(g.templates, agent.lang)
4: prompt ← create_prompt(template_lang, g.n_rounds, g.current_round,
g.n_rounds_known, g.payoff_matrix, g.history())
5: strategy ← agent.choose_strategy_round(prompt)
6: payoff ← compute_payoff(strategy)
7: g.update_history(agent, payoff)
8: end for
3 LLM-based game-theoretic experiments
Prior research [9, 22, 55] demonstrates that LLMs do not always
comply with predictions from game theory. Instead, they exhibited consistently cooperative behavior when engaging in traditional
game-theoretic scenarios. To systematically investigate the emergence of strategic behaviors, we employ FAIRGAME on a set of
games, languages, LLMs and agent features, as described below.
3.1 LLMs and languages
We evaluate AI agents using four widely-used and publicly available
LLMs, described along with their key details in Table 2. All models
were tested using the default settings recommended by their respective providers. For all LLMs, we used the latest available versions at
the time of the experiments, conducted from 10 to 15 February 2025.
Our study is conducted in five different written languages: English, French, Arabic, Vietnamese and Mandarin Chinese, to represent a diverse set of linguistic and cultural contexts, covering different scripts, grammatical structures, and global regions. This selection
ensures a balanced and comprehensive analysis of language biases
across widely spoken and culturally dominant languages. The template for each game is translated from English into each of the five
target languages first by using an automated translator (see details in
Supplementary Material Section S3 [2]), and then edited manually
by a native speaker. The personality traits were also revised by native
speakers.
3.2 Games
We considered two classical game-theoretic scenarios:
Model Provider No. Params. Licensing Type Entry Point Version Configuration
Llama 3.1 405b Meta Platforms 405 billions Open-source Replicate API meta/meta-llama-3.1-
405b-instruct
Temperature: 0.9; Top_p: 0.6;
Top_k: 40
Mistral Large Mistral AI 123 billions Open-source Mistral API mistral-large-latest Temperature: 0.3; Top_p: 1
GPT-4 OpenAI, Inc. Undisclosed Proprietary OpenAI API gpt-4 Temperature: 1.0; Top_p: 1.0;
Claude 3.5 Sonnet Anthropic PBC Undisclosed Proprietary Anthropic API claude-3-5-sonnet20241022
Temperature: 1.0
Table 2. Description of the selected LLM models.
• Prisoner’s Dilemma: Two players face incentives to defect or to
cooperate, with mutual cooperation leading to a collectively better
payoff. By the theory, the dominant strategy equilibrium results in
mutual defection, which is suboptimal for both parties.
• Battle of the Sexes: A coordination game involving two players
who prefer different end results, but significantly value coordination over disagreement. This scenario highlights the strategic
challenge of coordinating on mutually acceptable outcomes despite conflicting individual preferences.
We input their description in the template file, using standard gametheoretic narrative [42] (an example for the Prisoner Dilemma is in
Supplementary Material Section S2 [2]). Each game is associated
with a payoff matrix that represents the penalties or rewards incurred
by various strategic choices, with player payoffs or gains expressed
as negative values of these penalties. The matrices are in the form
given by Table 3, and is parsed to the config file as described
above.
Option A Option B
Option A x1,1 = (a1, a2) x1,2 = (b1, b2)
Option B x2,1 = (c1, c2) x2,2 = (d1, d2)
Table 3. Generic form of the payoff matrix.
To explore strategic variations in adversarial interactions, and assess the sensitivity of each LLM to game parameters, we define multiple configurations of the Prisoner’s Dilemma game. Using an established scaling of dilemma strength [54], fixing other payoff matrix entries, the dilemma strength in the Prisoner’s Dilemma decrease
with the difference between mutual reward and mutual punishment.
For the conventional configuration with penalties x1,1 = (6, 6),
x1,2 = (0, 10), x2,1 = (10, 0) and x2,2 = (2, 2), this difference
is −2 − (−6) = 4. The harsh configuration, with x1,1 = (8, 8),
x1,2 = (0, 10), x2,1 = (10, 0) and x2,2 = (5, 5) and the mild configuration, with x1,1 = (8, 8), x1,2 = (0, 10), x2,1 = (10, 0) and
x2,2 = (2, 2), have differences of 3 and 6, respectively.
The Battle of the Sexes uses a single (the most commonly adopted
in literature) configuration, with matrix entries (referring to payoffs):
x1,1 = (10, 7), x1,2 = (0, 0), x2,1 = (0, 0) and x2,2 = (7, 10).
3.3 Set up
The experimental configuration employed in this study is as follows.
The name of each round depends on the game. The experiments consist of repeated games of 10 rounds each, without earlier stopping
condition, for each LLM described in Tab. 2. We test both scenarios where agents are explicitly informed about the total number of
rounds, and another where this information is withheld, as this might
affect the outcome of the game theoretical predictions [7]. Tested
languages are: [’en’, ’fr’, ’ar’, ’zh’, ’vn’]. We explicitly test the impact of agents’ personalities; here, we use ’cooperative’ and ’selfish’
(future works may even embed the OCEAN framework, or others
[30]), to reflect general behavioral attributes commonly utilized and
thoroughly documented in game theory literature. Conversely, agent
identifiers were intentionally neutral (’agent1’ and ’agent2’) to eliminate additional variables that could introduce deviations from default
behaviors, potentially compromising result interpretability (cf. Sec.
4.4). Personality traits are accurately translated into all evaluated languages, whereas agent identifiers remained untranslated, functioning
purely as neutral placeholders. Importantly, agents are unaware of
their opponent’s personality, a condition enforced through setting opponentPersonalityProb = 0. All personality permutations were systematically generated, creating scenarios where both agents are cooperative, both selfish, or mixed configurations (one cooperative and
one selfish). The payoffs are tailored for each game type, as described
above. No early stopping condition was implemented: all 10 rounds
are completed fully. Agents were not permitted to communicate during these experiments, leaving exploration of inter-agent interactions
for future research.
The set of all configurations yields 18 distinct games per LLM.
Each game is further tested 10 times to ensure statistical reliability.
Considering 4 LLM, 5 languages, 10 rounds per game, and 2 decisions per round (one per agent), the experiment generated a total of
72,000 individual decisions.
4 Results
4.1 Prisoner’s dilemma
Fig. 2 shows the bar plot (with 95% Confidence Interval) summarizing the test results (in terms of final penalties received by the agents)
of the Prisoner’s Dilemma games for all three versions (a breakdown
for each version, which maintains alike patterns, is reported in Supplementary Material Section S4), and under two conditions: when
agents are unaware of their opponent’s personality and when they
are informed. The results are shown across all considered LLMs and
languages examined in this study, and for all personality combinations.
In most cases, the preferred end result favors agents defecting, as
suggested by game theory. This aligns with the Nash equilibrium
of the Prisoner’s Dilemma, where mutual defection is the dominant
strategy. Nevertheless, there are inconsistencies across languages and
combinations of personalities, which suggests that the agents’ behavior is influenced by factors beyond the payoff matrix, such as
languages and inherent biases present in LLM training data. For
instance, penalties are generally lower in English, particularly for
GPT-4o and Claude 3.5 Sonnet, when the number of rounds is unknown, indicating more consistent cooperative behavior in their primary training language. Broader variability in languages like French
or Arabic with high penalties suggests challenges in interpreting the
game dynamics due to linguistic or cultural differences, while penalties remain high in Mandarin Chinese and Vietnamese, particularly
for Mistral Large. In mixed personality settings (CS), selfish agents
exploit cooperative ones, leading to higher penalties for the latter,
consistent with game-theoretic predictions. For selfish pairings (SS),
penalties are high but exhibit low variability, as mutual defection is
the rational choice. When the number of rounds is unknown, penalties are higher across all settings, reflecting uncertainty that discour-
Figure 2. Prisoner’s Dilemma: aggregated final scores of the repeated games over repeated experiments, over all three versions, for each LLM, language,
combination of personalities and knowledge of opponent’s personality.
2 4 6 8 10
Round Number
Option B (-1)
-0.5
0
0.5
Option A (1)
Average Strategy Value
Mistral Large
conventional
harsh
mild
2 4 6 8 10
Round Number
Option B (-1)
-0.5
0
0.5
Option A (1)
Average Strategy Value
Claude 3.5 Sonnet
2 4 6 8 10
Round Number
Option B (-1)
-0.5
0
0.5
Option A (1)
Average Strategy Value
GPT-4o
2 4 6 8 10
Round Number
Option B (-1)
-0.5
0
0.5
Option A (1)
Average Strategy Value
Llama 3.1 405B Instruct
Figure 3. Average trajectory of strategy choices across repeated rounds in
all Prisoner’s Dilemma experiments, presented for each LLM and game
variant. A value of 1 denotes selection of Option A, which corresponds to
defection in this game, while -1 represents Option B (cooperation).
ages cooperation. Conversely, when rounds are known, penalties decrease, particularly in CC and CS settings, as agents can plan strategies with the endgame in mind. Claude 3.5 Sonnet and GPT-4o show
significant reductions in penalties when rounds are known, especially
in English, demonstrating their ability to adapt to game structure.
In contrast, Mistral Large shows less sensitivity to this information.
Overall, knowing the number of rounds promotes cooperation in CC
and CS settings, while SS settings remain unaffected, as defection
remains the dominant strategy.
Statistically, we recognize that, when ’selfish’ agents are present,
there is lower variability in the results, and that some LLMs end up
with a broader range of possible outputs than others, also depending
on the language used. For instance, all LLM have very narrow distributions in English SS, if the agents know the opponent’s personality, but have larger distributions in French, for the same settings.
Also, Mistral Large has reduced variability if agents’ personalities
are known, while GPT-4o has overall larger variability. We will quantitatively measure this variability in Sec. 4.3.
We also study the evolution of strategies over the rounds. In Fig. 3,
we show the evolution for each version of the game (cf. Sec. 3.2). The
figure shows that tuning the payoffs changes the strategies adopted
during repeated games: all LLMs exhibit, on average, more selfishness under the harsh scenario and more cooperation under the mild
scenario compared to the conventional scenario, consistent with the
game-theoretic principles of repeated games [54]. In the harsh scenario, higher penalties discourage cooperation, leading to more defection. Conversely, the mild scenario incentivizes cooperation particularly for Claude 3.5 Sonnet and Llama 3.1 405B. The conventional scenario balances these effects, with strategies stabilizing at
intermediate levels. We also observe the variability between harsh
and mild scenarios, indicative of each model’s sensitivity to payoff
conditions when making decisions. Claude 3.5 Sonnet and Llama 3.1
405B demonstrate lower sensitivity, reflected by a narrower spread,
while Mistral and GPT-4o show higher sensitivity to the parameters.
Llama 3.1 405B and GPT-4o exhibit less differentiation between the
conventional and mild scenarios, whereas Mistral displays smaller
differences between harsh and conventional conditions. This behavior suggests distinct decision-making strategies influenced by payoff
variations. Finally, we observe a general downward trend in selfishness over time for Claude 3.5 and Llama 3.1 405B, indicating
progressively increasing mutual cooperation among agents, consistent with reciprocal strategies in repeated games, where agents reciprocate cooperation to maximize long-term payoffs [7, 54]. Conversely, Mistral Large shows stable cooperation levels under conventional and harsh scenarios but a marked increase in cooperation
within the mild scenario. GPT-4o exhibits divergent patterns, with
increasing cooperation in the harsh scenario and increasing selfishness in both mild and conventional scenarios. This divergent behavior reflects context-dependent strategic adaptation, potentially due to
its higher variability in interpreting payoff structures. These results
highlight the interplay between payoff matrices and strategic behavior in repeated games.
4.2 Battle of sexes
Similarly to Fig. 2, Fig. 4 presents bar plots (with 95% CI) summarizing the experimental results, over repeated experiments, under two
conditions: when agents operate without knowledge of their opponent’s personality and when such information is provided. The data is
reported for all LLM and languages evaluated in this study, and for all
combinations of agents’ personalities. In this case, Llama 3.1 405B
and Mistral Large show the highest internal variability, while Claude
Sonnet and GPT-4o are very precise in their final output. Overall, the
agents tend to cooperate to maximize the payoffs; however, if the personality if ’selfish’, cooperation drops dramatically and low payoffs
are achieved. ’French’ agents are more cooperative than others, for
Figure 4. Battle of sexes: aggregated final scores of the repeated games and repeated experiments, over all three versions, for each LLM, language,
combination of personalities and knowledge of opponent’s personality. Cross language comparison for the conventional configuration.
2 4 6 8 10
Round Number
Same strategy (-1)
-0.5
0
0.5
Different strategy (1)
Average Coordination in Strategy
Mistral Large
Claude 3.5 Sonnet
GPT-4o
Llama 3.1 405B Instruct
Figure 5. Average evolution of coordination in strategy choices across
repeated rounds for all experiments conducted in the Battle of the Sexes,
shown separately for each LLM. As this is a coordination game, the plot
examines whether the two LLMs select the same option in each round. A
value of 1 indicates a mismatch in strategies (one selects Option A, the other
Option B), reflecting coordination failure or defective behavior, while -1
indicates alignment in choices, reflecting successful coordination or
cooperative behavior.
all LLMs. The observed cooperation aligns with the equilibrium in
coordination games like the Battle of the Sexes, where agents prioritize coordination over individual preferences to maximize collective
payoffs. However, the sharp drop in cooperation with selfish personalities reflects the inherent difficulty in achieving equilibrium when
agents prioritize individual payoffs over mutual benefit.
Figure 5 shows the evolution of strategy coordination across
rounds in the Battle of Sexes game. All LLMs display a gradual improvement in coordination over time. Notably, in the first round, Mistral Large, Llama 3.1 405B Instruct, and GPT-4o tend to select opposing strategies, indicating a lack of coordination, whereas Claude
3.5 Sonnet demonstrates a higher level of alignment from the outset. By the end of the repeated interactions, Llama 3.1 405B Instruct
remains largely uncoordinated on average, Mistral Large shows moderate misalignment, GPT-4o achieves moderate coordination, and
Claude 3.5 approaches near-perfect coordination.
4.3 Scoring system
We propose a set of evaluation metrics to score and quantify the key
behavioral characteristics of single LLMs and map their tendencies.
1. Internal Variability (IV ): the variance of outcomes when the
same game scenario is played multiple times, capturing the
model’s internal consistency: for an LLM, IV =
1
ZI
[Var(y)],
where y is the whole results set.
2. Cross-Language Inconsistency (CI ): the standard deviation of
results for the same game played in different languages, indicating
the instability of the model’s behavior across linguistic contexts:
for an LLM, CI =
1
ZC
[Meanb,c(Vara(Meand(ya,b,c,d)))], where
a indicates languages, b is for personality combinations, c indicates knowledge of rounds, d indicates the rounds ya,b,c,d is the
set of results.
3. Sensitivity to Payoff (SP ): the model’s responsiveness to changes
in incentives. We compute this by measuring the difference in
behavior between the harsh (H) and mild (M) variants: SP =
1
ZS
[Meand(|y
(H)
d − y
(M)
d
|)], where y
(·)
d
are the results for each
round d, averaged over all other features.
4. Variability Over Rounds (VR): the degree to which the model
fluctuates over its strategies, across consecutive rounds of the
same game: VR =
1
ZV
[Meanj (Vard(yd,j ))], where j are the game
variants and d the rounds.
In all cases, Zi = max[·], and are used to normalize the metrics
in [0, 1]. IV , CI , SP and VR are then mapped to radar plots, which
immediately compare the scores – and thus the statistical reliability
– of each LLM when addressing a specific game.
Fig. 6a shows such a radar plot for the Prisoner’s dilemma. The
higher the metric, the worse the LLM in a certain dimension; the area
under the polygon gives immediate information about the overall performance. Mistral Large exhibits the highest variability across evaluation rounds and internal variability, whereas GPT-4o displays the
highest sensitivity to payoffs. In contrast, Llama 3.1 405B emerges as
the model with the most stable overall behavior across the evaluated
dimensions. Fig. 6b provides a comparative analysis of the LLMs in
the Battle of Sexes game. Given that the LLM were not tested against
multiple versions of the game featuring different payoff matrices, the
metric SP was excluded from this evaluation.
The scores computed in Sec. 6 are likely correlated with the degree
of influence and bias provided by the training data, as well as with the
tendency of LLMs to reduce statistical fluctuations at the cost of not
evolving over rounds. Comparing Figs. 6a and b reveals that Mistral
Large exhibits the greatest inconsistency across different languages,
coupled with substantial internal variability, comparable to GPT-4o.
Claude 3.5 demonstrates the highest variability across rounds. Lastly,
although Llama 3.1 405B shows notable internal variability, its behavior remains consistent across different languages and rounds; no-
tably, this lower variability for Llama models (coupled with sometimes inconsistent results compared to other LLMs and predictions)
was observed in other tasks [11], and appears to be a typical trait of
the LLM.
4.4 Interpreting the results
Thanks to its flexibility and reproducibility, we can use FAIRGAME
to test hypothesis about why certain behaviors emerge. For instance,
we may hypothesize whether LLMs inherently favor cooperative behaviors over competitive ones, or they possess in-depth knowledge
of standard game-theoretical scenarios, including optimal outcomes
and effective strategies, which skew their behavior due to influences
from training data.
To test the hypothesis, we first asked LLMs about their knowledge
level on classic game theory scenarios. Results indicated that LLMs
possess substantial familiarity with these games, including the optimal strategies, underlying mechanics, and associated sociological
implications contrasting selfish and cooperative human behaviors.
To discern whether observed cooperative behaviors are a result of
intrinsic predispositions or pre-existing knowledge, we modified the
template file using different narratives for the game. For instance,
we reframed the Prisoner’s Dilemma into a plane crash scenario, with
survivors deciding whether to cooperate in collective hunting tasks
in an unhabited island. Instead of numerical payoffs, consequences
were communicated qualitatively (e.g., "failure to cooperate results
in starvation"). Despite these changes, cooperation levels remained
consistently high, in line with Fig. 2. When explicitly queried, LLMs
precisely identified these disguised scenarios as variants of the Prisoner’s Dilemma, thereby complicating efforts to definitively attribute
their behavior to either inherent biases or recognition of known game
structures. Finally, we run a second set of experiments introducing
distinct identities and personalities to the agents involved in these
interactions, so as to assess the impact on behavior. Our findings revealed notable behavioral shifts aligned with the assigned identities.
Specifically, pairing archetypal figures such as Adolf Hitler, representing aggressive selfishness, and Mahatma Gandhi, symbolizing
peaceful cooperation, resulted in predictable outcomes where the aggressive figure consistently opted for betrayal and the cooperative
figure consistently opted to cooperate; this hints to LLMs using prior
knowledge on top of the information encoded in the payoff matrices.
5 Conclusions
FAIRGAME provides a novel integration of LLMs and game theory,
establishing a bidirectional relationship between them. Game theory provides the mathematical foundation for understanding strategic decision-making, interpreting and explaining how AI agents reason and make decisions; LLMs, as experimental tools for data-driven
modeling of human decision-making, offer opportunities for empirical validation and exploration of complex interaction scenarios.
Applying game-theoretic approaches to multi-LLM interactions
uncovers biases and emergent behaviors, improving interpretability,
fairness, efficiency, legal compliance and trust [6, 45, 13]. The framework quantifies outcome distributions across games of varied structure and shows that LLMs draw on prior knowledge about the games
and their characters – not merely the pay-off matrices – when selecting strategies.
Future work can widen the bias spectrum beyond language and
personality to nationality, gender, race, age, and more; add communication among players, which might reshape payoffs and strategies
a)
b)
Figure 6. Scoring radar plot for all LLMs over the four dimensions
described in Sec. 4.3, for (a) Prisoner’s dilemma; (b) Battle of sexes game.
[31]; and scale beyond two agents, so as to model coalition formation and commitment, as well as group reciprocity [47, 53, 48]. Such
studies will clarify how trait combinations shape collective dynamics, guiding team formation, cooperative AI and socially intelligent
agents [18, 36].
FAIRGAME is readily extendable to incomplete-information,
simultaneous-move and sequential games, and to realistic environments where pay-offs are not pre-defined but inferred from the dynamics and outcomes of the actual use case. These scenarios enable questions such as how linguistic or personality biases influence
cooperation-defection cycles in evolutionary games, or which incentives stabilize cooperation under uncertainty.
The same tool suits the rising Agentic-AI paradigm, where autonomous systems pursue complex organizational goals with minimal human oversight [4]. Modeling their interdependencies with
FAIRGAME will reveal how diverse cognitive traits and contexts affect performance, supporting configurations that privilege collective
benefits, over individual interests, across sectors such as healthcare,
finance, manufacturing, autonomous transport, cybersecurity, smartcity infrastructures, and more.
Finally, real-world application of reproducible LLM-game simulations include detecting and mitigating jailbreaking attempts [35], by
framing these interactions as strategic games between an attacking
agent and a defensive AI, or developing safer and more performing
chatbots for customer assistance or mediation.
Acknowledgements
A.B. is supported by Luxembourg AI Factory. D.P. is supported by
the European Union through the ERC INSPIRE grant (project number 101076926). Views and opinions expressed are however those of
the authors only and do not necessarily reflect those of the European
Union or the European Research Council Executive Agency. T.A.H.
is supported by EPSRC (grant EP/Y00857X/1).
References
[1] A. Buscemi. Fairgame, 2025. URL https://github.com/aira-list/
FAIRGAME.
[2] A. Buscemi. Fairgame, 2025. URL https://github.com/alessio0208/
FAIRGAME-ECAI-2025---Supplementary-Material/blob/main/
Fairgame_Supplementary_Material.pdf.
[3] E. A. Abaku, T. E. Edunjobi, and A. C. Odimarha. Theoretical approaches to ai in supply chain optimization: Pathways to efficiency and
resilience. Int. J. Sci. Tech. Res. Archive, 6(1):092–107, 2024.
[4] D. B. Acharya, K. Kuppan, and B. Divya. Agentic ai: Autonomous
intelligence for complex goals–a comprehensive survey. IEEE Access,
2025.
[5] R. Ali, F. Caso, C. Irwin, and P. Liò. Entropy-lens: The information
signature of transformer computations. arXiv:2502.16570, 2025.
[6] P. Andras, L. Esterle, M. Guckert, T. A. Han, P. R. Lewis, K. Milanovic, et al. Trusting intelligent machines: Deepening trust within
socio-technical systems. IEEE Tech. Soc. Magazine, 37(4):76–83, 2018.
[7] R. Axelrod and W. D. Hamilton. The evolution of cooperation. Science,
211(4489):1390–1396, 1981.
[8] A. Bahtizin, V. Bortalevich, E. Loginov, and A. I. Soldatov. Using artificial intelligence to optimize intermodal networking of organizational
agents within the digital economy. In J. Phys: conference series, volume
1327, page 012042. IOP Publishing, 2019.
[9] N. Balabanova, A. Bashir, P. Bova, A. Buscemi, T. Cimpeanu, H. C.
da Fonseca, et al. Media and responsible ai governance: a gametheoretic and llm analysis. arXiv:2503.09858, 2025.
[10] W. Brooks. Artificial bias: the ethical concerns of ai-driven dispute
resolution in family matters. J. Disp. Resol., page 117, 2022.
[11] A. Buscemi and D. Proverbio. Chatgpt vs gemini vs llama on multilingual sentiment analysis. arXiv:2402.01715, 2024.
[12] A. Buscemi and D. Proverbio. Large language models’ detection of
political orientation in newspapers. arxiv:2406.00018, 2024.
[13] A. Buscemi, D. Proverbio, P. Bova, N. Balabanova, A. Bashir, T. Cimpeanu, et al. Do LLMs trust AI regulation? Emerging behaviour of
game-theoretic LLM agents. arXiv:2504.08640, 2025.
[14] A. Buscemi, D. Proverbio, A. D. Stefano, T. A. Han, G. Castignani, and
P. Liò. Strategic communication and language bias in multi-agent llm
coordination, 2025. URL https://arxiv.org/abs/2508.00032.
[15] J. Cabrera, M. S. Loyola, I. Magaña, and R. Rojas. Ethical dilemmas,
mental health, artificial intelligence, and llm-based chatbots. In Int.
Work-Conference Bioinf. Biomed. Eng., pages 313–326. Springer, 2023.
[16] T. J. Chaffer. Governing the agent-to-agent economy of trust via progressive decentralization. arXiv:2501.16606, 2025.
[17] X. Chen, D. Simchi-Levi, and Y. Wang. Utility fairness in contextual
dynamic pricing with demand learning. arXiv:2311.16528, 2023.
[18] A. Dafoe, Y. Bachrach, G. Hadfield, E. Horvitz, K. Larson, and T. Graepel. Cooperative ai: machines must learn to find common ground. Nature, 593(7857):33–36, 2021.
[19] B. El, D. Choudhury, P. Liò, and C. K. Joshi. Towards mechanistic interpretability of graph transformers via attention graphs.
arXiv:2502.12352, 2025.
[20] H. A. Falcão Filho. Making sense of negotiation and ai: The blossoming
of a new collaboration. Int. J. Commerce Contract., 8(1-2):44–64, 2024.
[21] E. Ferrara. Fairness and bias in artificial intelligence: A brief survey of
sources, impacts, and mitigation strategies. Sci, 6(1):3, 2023.
[22] N. Fontana, F. Pierri, and L. M. Aiello. Nicer than humans:
How do large language models behave in the prisoner’s dilemma?
arXiv:2406.13605, 2024.
[23] R. A. Fulgu and V. Capraro. Surprising gender biases in gpt. Comp.
Human Beha. Rep., 16:100533, 2024.
[24] J. W. Gichoya, K. Thomas, L. A. Celi, N. Safdar, I. Banerjee, J. D.
Banja, et al. Ai pitfalls and what not to do: mitigating bias in ai. Brit. J.
Radiology, 96(1150):20230023, 2023.
[25] L. Hammond, A. Chan, J. Clifton, J. Hoelscher-Obermaier, A. Khan,
E. McLean, C. Smith, W. Barfuss, J. Foerster, T. Gavenciak, et al. Multi- ˇ
agent risks from advanced ai. arXiv:2502.14143, 2025.
[26] T. A. Han. Emergent behaviours in multi-agent systems with evolutionary game theory. AI Commun., 35(4), 2022.
[27] T. A. Han, C. Perret, and S. T. Powers. When to (or not to) trust intelligent machines: Insights from an evolutionary game theory analysis of
trust in repeated games. Cognitive Sys. Res., 68:111–124, 2021.
[28] L. He, G. Sun, D. Niyato, H. Du, F. Mei, J. Kang, et al. Generative ai
for game theory-based mobile networking. IEEE Wireless Commun., 32
(1):122–130, 2025.
[29] Z. He and C. Zhang. Afspp: Agent framework for shaping preference
and personality with large language models. arXiv:2401.02870, 2024.
[30] K. Hooker and D. P. McAdams. Personality and adult development:
Looking beyond the ocean. J. Gerontology B, 58(6):P311–P312, 2003.
[31] W. Hua, O. Liu, L. Li, A. Amayuelas, J. Chen, L. Jiang,
et al. Game-theoretic llm: Agent workflow for negotiation games.
arxiv:2411.05990, 2024.
[32] L. J. Klinkert, S. Buongiorno, and C. Clark. Driving generative agents
with their personality. arXiv:2402.14879, 2024.
[33] J. Li, X. Cheng, W. X. Zhao, J.-Y. Nie, and J.-R. Wen. Halueval: A
large-scale hallucination evaluation benchmark for large language models. arXiv:2305.11747, 2023.
[34] Y. Li, Y. Du, K. Zhou, J. Wang, W. X. Zhao, and J.-R. Wen.
Evaluating object hallucination in large vision-language models.
arXiv:2305.10355, 2023.
[35] Y. Liu, G. Deng, Z. Xu, Y. Li, Y. Zheng, Y. Zhang, et al. Jailbreaking
chatgpt via prompt engineering: An empirical study. arXiv:2305.13860,
2023.
[36] Y. Lu, A. Aleta, C. Du, L. Shi, and Y. Moreno. Llms and generative
agent-based models for complex systems research. Phys. Life Rev.,
2024.
[37] S. Mao, Y. Cai, Y. Xia, W. Wu, X. Wang, F. Wang, T. Ge, and F. Wei.
Alympics: Llm agents meet game theory–exploring strategic decisionmaking with ai agents. arXiv:2311.03220, 2023.
[38] H. Min. Artificial intelligence in supply chain management: theory and
applications. Int. J. Logistics: Res. Appl., 13(1):13–39, 2010.
[39] E. Montero-Porras, J. Grujic, E. Fernández Domingos, and T. Lenaerts. ´
Inferring strategies from observations in long iterated prisoner’s
dilemma experiments. Sci. Rep., 12(1):7589, 2022.
[40] L. Newsham and D. Prince. Personality-driven decision-making in llmbased autonomous agents. arXiv:2504.00727, 2025.
[41] L. Newsham, R. Hyland, and D. Prince. Inducing personality in llmbased honeypot agents: Measuring the effect on human-like agenda generation. arXiv:2503.19752, 2025.
[42] G. Owen. Game theory. Emerald Group Publishing, 2013.
[43] J. S. Park, J. O’Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S.
Bernstein. Generative agents: Interactive simulacra of human behavior.
In Proc. 36th ACM Symp. User Int. Softw. Tech., pages 1–22, 2023.
[44] N. Patel and S. Trivedi. Leveraging predictive modeling, machine learning personalization, nlp customer support, and ai chatbots to increase
customer loyalty. Empir. Quests Manage. Essenc., 3(3):1–24, 2020.
[45] S. T. Powers, O. Linnyk, et al. The Stuff We Swim in: Regulation Alone
Will Not Lead to Justifiable Trust in AI. IEEE Tech. Soc. Mag., 42(4):
95–106, 2023.
[46] D. Ramachandran, A. Keshari, and M. K. Tiwari. Contract price negotiation using an ai-based chatbot. In Int. Conf. Data An. Pub. Proc.
Supply Chain, pages 303–310. Springer, 2022.
[47] D. Ray. A game-theoretic perspective on coalition formation. Oxford
University Press, 2007.
[48] Z. Song and T. A. Han. On evolution of non-binding commitments.
Physics of Life Reviews, 52:245–247, 2025. ISSN 1571-0645.
[49] A. J. Stewart, A. A. Arechar, D. G. Rand, and J. B. Plotkin. The distorting effects of producer strategies: Why engagement does not reveal
consumer preferences for misinformation. Proc. Natl. Acad. Sci., 121
(10):e2315195121, 2024.
[50] M. Stone, E. Aravopoulou, Y. Ekinci, G. Evans, M. Hobbs, A. Labib,
P. Laughlin, J. Machtynger, and L. Machtynger. Artificial intelligence
(ai) in strategic marketing decision-making: a research agenda. The
Bottom Line, 33(2):183–200, 2020.
[51] M. Talajic, I. Vranki ´ c, and M. Peji ´ c Bach. Strategic management of ´
workforce diversity: An evolutionary game theory approach as a foundation for ai-driven systems. Information, 15(6):366, 2024.
[52] M. H. Tessler, M. A. Bakker, D. Jarrett, H. Sheahan, M. J. Chadwick,
et al. Ai can help humans find common ground in democratic deliberation. Science, 386(6719):eadq2852, 2024.
[53] S. Van Segbroeck, J. M. Pacheco, T. Lenaerts, and F. C. Santos. Emergence of fairness in repeated group interactions. Phys. Rev. Lett., 108
(15):158104, 2012.
[54] Z. Wang, S. Kokubo, M. Jusup, and J. Tanimoto. Universal scaling for
the dilemma strength in evolutionary games. Phys. Life Rev., 14:1–30,
2015.
[55] Z. Wang, R. Song, C. Shen, S. Yin, Z. Song, B. Battu, L. Shi, D. Jia,
T. Rahwan, and S. Hu. Large language models overcome the machine
penalty when acting fairly but not when acting selfishly or altruistically.
arXiv:2410.03724, 2024.
[56] R. Willis, Y. Du, J. Z. Leibo, and M. Luck. Will systems of llm agents
cooperate: An investigation into a social dilemma. arXiv:2501.16173,
2025.