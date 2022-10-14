# A Trained Adversarial AI Competitor (aTaac)

The aTaac system was developed as part of research conducted on automated penetration testing 
at Johns Hopkins University by [Samra Kasim](https://github.com/skasim/aTaac), [Nawal Valliani](https://github.com/nawalvalliani), [Nelson Ka Ki Wong](https://github.com/trace86), and Shahin Samadi.

The system utilizes Alpha-Beta Minimax and DNN for AI gameplay. The former code is based on code from the repo by 
[Clederson Cruz](https://github.com/Cledersonbc/tic-tac-toe-minimax) and the DNN was developed based on code by 
[Daniel Sauble](https://github.com/djsauble/tic-tac-toe-ai)



## Citation Request
aTaac is available for research use under GNU Public License. If utilizing aTaac code or its derivative resources, please cite the following:

> S. Kasim, N. Valliani, N. K. K. Wong, S. Samadi, L. Watkins, and A. Rubin, “Cybersecurity as a Tic-Tac-Toe Game Using Autonomous Forwards (Attacking) And Backwards (Defending) Penetration Testing in a Cyber Adversarial Artificial Intelligence System,” 2022.
> S. Kasim, N. Valliani, N. K. K. Wong, and S. Samadi, aTaac: A Trained Adversarial AI Competitor system. 2022. [Online]. Available: https://github.com/skasim/aTaac

Bibtex:
```
@inproceedings{KasimEtAl2022,
  author = {Samra Kasim and 
            Nawal Valliani and 
            Nelson Ka Ki Wong and 
            Shahin Samadi and
            Lanier Watkins and
            Aviel Rubin},
    title = {{C}ybersecurity as a {T}ic-{T}ac-{T}oe {G}ame {U}sing
            {A}utonomous {F}orwards ({A}ttacking) {A}nd {B}ackwards ({D}efending) {P}enetration {T}esting in a {C}yber {A}dversarial {A}rtificial {I}ntelligence {S}ystem},
    year = {2022},
    booktitle = {2022 IEEE  International Conference of SNIKOM, Laguboti, Sumatera Utara, Indonesia}
}

@misc{aTaacCode,
  author = {Samra Kasim and 
            Nawal Valliani and 
            Nelson Ka Ki Wong and 
            Shahin Samadi},
    title = {a{T}aac: {A} {T}rained {A}dversarial {AI} {C}ompetitor system},
    year = {2022},
    url = {https://github.com/skasim/aTaac},
}
```

## Running aTaac
To run game simulations:
* Clone this repo
* In `aTaac` directory, create a `.env` file populated as below
```.env
# Key Files
PORTSCAN_XML="nmap/portscan_out.xml"
ATTACK_PORTS_PK = "attack_ports/attack_ports.pickle"
COMMANDS_CSV="vulnerability_execute/commands2.csv"
VULNERABILITY_SCRIPTS_DIR = "vulnerability_scripts"
ROOT_PATH = "/opt/capstone/jhu-aai/aTaac/io"
GAMEPLAY_5x5 = "gameplay/output_5x5.csv"
GAMEPLAY_3x3 = "gameplay/output_3x3.csv"
# Game Parameters
OUTPUT_DELAY=1  # python-dotenv does not parse boolean, so 1 == True and 0 == False
GENERATE_DATA=0 # python-dotenv does not parse boolean, so 1 == True and 0 == False
VERBOSE_OUTPUT=1 # python-dotenv does not parse boolean, so 1 == True and 0 == False
AI_VS_HUMAN=0 # python-dotenv does not parse boolean, so 1 == True and 0 == False
HUMAN_PLAYS=2 # 1 == ATTACK(X), 2 == DEFENSE(O)
NUMBER_OF_GAMES=1
LENGTH_OF_BOARD=5
# Chaos Agent
ATTACKER_SKILL_LEVEL=5 # ranges from 0 (low-skilled) to 5 (high-skilled)
DEFENDER_SKILL_LEVEL=5 # ranges from 0 (low-skilled) to 5 (high-skilled)
# Gameplay Models
PLAYER_1_ALGO=minimax   # choice of dnn, minimax
PLAYER_2_ALGO=minimax   # choice of dnn, minimax
# Docker
ATTACK="kali-everything"
DEFENSE="metasploitable2"
DOCKER=0 # python-dotenv does not parse boolean, so 1 == True and 0 == False
# EXPERIMENTATION
RUN_EXPERIMENTS=0 # python-dotenv does not parse boolean, so 1 == True and 0 == False
EXPERIMENT_BOARD_LEN=3
EXPERIMENT_NUM_GAMES=1
```
* Update `NUMBER_OF_GAMES` and `LENGTH_OF_BOARD` variables as necessary
* Run `init_game.py`

## Running with Docker
To run code in Docker
* Clone this repo
* Add `.env` file to `aTaac` directory, see above for content
* Update volume path to your local machine in `docker-compose.yml`
* Run `docker-compose up`
* Run `docker exec -it $container_name` and `cd` to `/opt/capstone/jhu-aai/aTaac` directory and run `python init_game.py`

