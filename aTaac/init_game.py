import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys
import keras
import game_play as gp
from dotenv import load_dotenv
import random
from datetime import datetime
from script_launcher import ScriptLauncher
from docker_move import start_game_docker, end_game_docker
import logging
import uuid
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

sys.path.insert(1, os.getcwd())

load_dotenv()
# load vales from .env
root_path = os.getenv('ROOT_PATH')
docker = int(os.getenv("DOCKER"))
human = True if int(os.getenv("AI_VS_HUMAN")) == 1 else False
human_player = int(os.getenv("HUMAN_PLAYS"))
run_experiments = True if int(os.getenv("RUN_EXPERIMENTS")) == 1 else False
experiment_board_len = int(os.getenv("EXPERIMENT_BOARD_LEN"))
experiment_num_games = int(os.getenv("EXPERIMENT_NUM_GAMES"))
gameplay_board = int(os.getenv("LENGTH_OF_BOARD"))
gameplay_3_log = os.getenv("GAMEPLAY_3x3")
gameplay_5_log = os.getenv("GAMEPLAY_5x5")

#disable urllib3 messages
urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.CRITICAL)

#disable tensorflow messages
urllib3_logger = logging.getLogger('tensorflow')
urllib3_logger.setLevel(logging.CRITICAL)

#configure google drive
gauth = GoogleAuth()
drive = GoogleDrive(gauth)  

#configuring logger
filename = datetime.now().strftime('%Y%m%d%H%M_container_log_file.log')
filepath = f'{root_path}/container_moves/{filename}'
handler = logging.FileHandler(filepath, 'w', 'utf-8')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%H:%M:%S') # or whatever
handler.setFormatter(formatter) # Pass handler as a parameter, not assign
root_logger.addHandler(handler)


def play_games(len_board=None, num_games=None, attacker_skill_level=None, defender_skill_level=None, player1_algo=None,
               player2_algo=None, gameplay_outcsv=None, generate_data=None, delay_output=None, have_env=True):
    if not have_env:
        len_board = len_board
        num_games = num_games
        attacker_skill_level = attacker_skill_level
        defender_skill_level = defender_skill_level
        player1_algo = player1_algo
        player2_algo = player2_algo
        gameplay_outcsv = gameplay_outcsv
        generate_data = True
        delay_output = False
        verbose_output = False
    else:
        len_board = int(os.getenv("LENGTH_OF_BOARD"))
        num_games = int(os.getenv("NUMBER_OF_GAMES"))
        attacker_skill_level = int(os.getenv("ATTACKER_SKILL_LEVEL"))
        defender_skill_level = int(os.getenv("DEFENDER_SKILL_LEVEL"))
        player1_algo = str(os.getenv("PLAYER_1_ALGO"))
        player2_algo = str(os.getenv("PLAYER_2_ALGO"))
        gameplay_outcsv = f"{os.getenv('GAMEPLAY_3x3')}_{datetime.now().strftime('%Y%m%d%H%M')}.csv" if len_board == 3 else f"{os.getenv('GAMEPLAY_5x5')}_{datetime.now().strftime('%Y%m%d%H%M')}.csv"
        delay_output = True if int(os.getenv("OUTPUT_DELAY")) == 1 else False
        generate_data = True if int(os.getenv("GENERATE_DATA")) == 1 else False
        verbose_output = True if int(os.getenv("VERBOSE_OUTPUT")) == 1 else False

    model_3x3 = keras.models.load_model("AlphaToe3")
    model_5x5 = keras.models.load_model("AlphaToe5")
    print("Loaded Keras models.")
    logging.info("Loaded Keras models.")

    for i in range(1, num_games + 1):
        #generate uuid
        game_id = uuid.uuid4()
        logging.info(f"------------------------------------------------------------------------")
        logging.info(f"playing game {i} of {num_games}...")
        logging.info(f"game id: {game_id}")
        print(f"playing game {i} of {num_games}...")
        print(f"game id: {game_id}")
        # start with clean slate
        random.seed(datetime.now())
        rnd1, rnd2 = random.uniform(0, 1), random.uniform(0, 1)
        exploit_tracker = {
            "exploit_initiated": False,
            "set_initiated": False
        }
        launcher = ScriptLauncher()
        
        if len_board == 3:
            if human:
                print("Running AI vs Human 3x3 game play")
                logging.info("Running AI vs Human 3x3 game play")
                winner, board, chaos_count = gp.ai_vs_human(model_3x3, rnd1=rnd1, rnd2=rnd2, len_board=len_board,
                                               verbose=verbose_output, delay=delay_output, generate_data=generate_data,
                                               human_plays=human_player, exploit_tracker=exploit_tracker,
                                               launcher=launcher, docker=docker, attacker_skill=attacker_skill_level,
                                               defender_skill=defender_skill_level, player1_algo=player1_algo,
                                               player2_algo=player2_algo, game_id=game_id,
                                               gameplay_outcsv=gameplay_outcsv)
            else:
                print("Running AI vs AI 3x3 game play")
                logging.info("Running AI vs AI 3x3 game play")
                winner, board, chaos_count = gp.ai_vs_ai(model_3x3, rnd1=rnd1, rnd2=rnd2, len_board=len_board, verbose=verbose_output,
                                            delay=delay_output, generate_data=generate_data,
                                            exploit_tracker=exploit_tracker, launcher=launcher, docker=docker,
                                            attacker_skill=attacker_skill_level, defender_skill=defender_skill_level,
                                            player1_algo=player1_algo, player2_algo=player2_algo, game_id=game_id,
                                            gameplay_outcsv=gameplay_outcsv)

            gp.printWinner(winner)
            logging.info(f"Winner: {winner} | Attack Skill Level: {attacker_skill_level} | Defense Skill Level: {defender_skill_level}")
            logging.info(f"Chaos Occured: | {chaos_count[0]} | {chaos_count[1]}")

        elif len_board == 5:
            if human:
                print("Running AI vs Human 5x5 game play")
                logging.info("Running AI vs Human 5x5 game play")
                winner, board, chaos_count = gp.ai_vs_human(model_5x5, rnd1=rnd1, rnd2=rnd2, len_board=len_board,
                                               verbose=verbose_output, delay=delay_output, generate_data=generate_data,
                                               human_plays=human_player, exploit_tracker=exploit_tracker,
                                               launcher=launcher, docker=docker, attacker_skill=attacker_skill_level,
                                               defender_skill=defender_skill_level, player1_algo=player1_algo,
                                               player2_algo=player2_algo, game_id=game_id, gameplay_outcsv=gameplay_outcsv)
            else:
                print("Running AI vs AI 5x5 game play")
                logging.info("Running AI vs AI 5x5 game play")
                winner, board, chaos_count = gp.ai_vs_ai(model_5x5, rnd1=rnd1, rnd2=rnd2, len_board=len_board, verbose=verbose_output,
                                            delay=delay_output, generate_data=generate_data,
                                            exploit_tracker=exploit_tracker, launcher=launcher, docker=docker,
                                            attacker_skill=attacker_skill_level, defender_skill=defender_skill_level,
                                            player1_algo=player1_algo, player2_algo=player2_algo, game_id=game_id,
                                            gameplay_outcsv=gameplay_outcsv)
                
            gp.printWinner(winner)
            logging.info(f"Winner: {winner} | Attack Skill Level: {attacker_skill_level} | Defense Skill Level: {defender_skill_level}")
            logging.info(f"Chaos Occured: | {chaos_count[0]} | {chaos_count[1]}")
        else:
            raise ValueError(f"We can't run a {len_board}x{len_board} game")


def experiment(len_board, num_games):
    algorithms = [["minimax", "minimax"], ["dnn", "dnn"], ["minimax", "dnn"], ["dnn", "minimax"]]
    attacker_skills = [5, 4, 3, 2, 1, 0]
    defender_skills = [5, 4, 3, 2, 1, 0]
    for algo in algorithms:
        attacker_algo = algo[0]
        defender_algo = algo[1]
        for attacker_skill_level in attacker_skills:
            for defender_skill_level in defender_skills:
                outfile = f"gameplay/{len_board}x{len_board}game_p1{attacker_algo}{attacker_skill_level}_p2{defender_algo}{defender_skill_level}_{datetime.now().strftime('%Y_%m_%d-%I_%M_%S_%p')}.csv"
                print(f"generating file {outfile}")
                play_games(
                    len_board=len_board,
                    num_games=num_games,
                    attacker_skill_level=attacker_skill_level,
                    defender_skill_level=defender_skill_level,
                    player1_algo=attacker_algo,
                    player2_algo=defender_algo,
                    gameplay_outcsv=outfile,
                    generate_data=True,
                    delay_output=False,
                    have_env=False
                )

def upload_results():
    print('uploading...')

    #Create Folder
    folder_name = datetime.now().strftime('%Y%m%d%H%M')
    file_metadata = {
    'title': folder_name,
    'parents': [{'id': '1dgQp8GawoICEwj1Uh4U8OJQNsLIiZZzs'}],
    'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.CreateFile(file_metadata)
    folder.Upload()

    #get files to upload
    if gameplay_board == 3:
        gameplay_log_path = root_path + '/' + gameplay_3_log
    else:
        gameplay_log_path = root_path + '/' + gameplay_5_log
    upload_file_list = [filepath, gameplay_log_path]

    #upload files to google drive
    for upload_file in upload_file_list:
        gfile = drive.CreateFile({'parents': [{'id': folder['id']}]})
        # Read file and set it as the content of this instance.
        gfile.SetContentFile(upload_file)
        gfile.Upload() # Upload the file.
    
    print('upload done...')

if run_experiments:
    experiment(len_board=experiment_board_len, num_games=experiment_num_games)
    # upload_results()
    end_game_docker()
else:
    play_games(have_env=True)
    # upload_results()
    if docker == 1:
        end_game_docker()
