from agt_server.agents.base_agents.lsvm_agent import MyLSVMAgent
from agt_server.local_games.lsvm_arena import LSVMArena
from agt_server.agents.test_agents.lsvm.min_bidder.my_agent import MinBidAgent
from agt_server.agents.test_agents.lsvm.jump_bidder.jump_bidder import JumpBidder
from agt_server.agents.test_agents.lsvm.truthful_bidder.my_agent import TruthfulBidder
import time
import os
import random
import gzip
import json
from collections import deque
from path_utils import path_from_local_root

NAME = "idk"

def comparator(e):
    return e["value"]

class MyAgent(MyLSVMAgent):
    def setup(self):
        #TODO: Fill out with anything you want to initialize each auction
        #------Utility-------------#
        self.goods_to_consider = {"A", "B", "C", "D", "E", "F", 
                                  "G", "H", "I", "J", "K", "L", 
                                  "M", "N", "O", "P", "Q", "R"}
        self.index = [[chr(i + 65 + 6 * j) for i in range(6)] for j in range(3)]
        #------For national--------#
        self.border = {"A", "B", "C", "D", "E", "F", 
                       "G",                     "L", 
                       "M", "N", "O", "P", "Q", "R"}
        self.BORDER_SHADE = 0.9
        self.OUTER_SHADE = 0.7
        self.GRACE_PERIOD = 5
        self.counter = 0
        #------For regional--------#
        self.top_priority = set()
        self.high_priority = set()
        self.mid_priority = set()
        self.low_priority = set()
        self.TOP_SHADE = 0.9
        self.HIGH_SHADE = 0.6
        self.MID_SHADE = 0.4
        self.LOW_SHADE = 0.3
        self.TOP_SIZE = 3

    def validate_coord(self, x, y):
        return (x >= 0 and x < len(self.index)) and (y >= 0 and y < len(self.index[0]))
    
    def determine_priority(self, init_size):
        if (self.is_national_bidder() or init_size > 5):
            return
        valuations = self.get_valuations()
        coords = self.get_goods_to_index()

        center = self.get_regional_good()
        centerCoord = coords[center]
        self.top_priority.add(center)

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        seen = set()
        seen.add(centerCoord)
        queue = deque()
        if (init_size > 1):
            init_size -= 1
            to_add = []
            for d in directions:
                x = centerCoord[0] + d[0]
                y = centerCoord[1] + d[1]
                if (self.validate_coord(x, y)):
                    to_add.append({"id": self.index[x][y], "value": valuations[self.index[x][y]]})
                    seen.add((x, y))
                    queue.append((x, y))
            to_add.sort(key=comparator)
            while (init_size > 0):
                self.top_priority.add(to_add.pop()["id"])
                init_size -= 1
        
        level = 0
        while (len(queue) > 0):
            n = len(queue)
            for _ in range(n):
                curr = queue.popleft()
                if (level == 1):
                    self.high_priority.add(self.index[curr[0]][curr[1]])
                elif (level == 2):
                    self.mid_priority.add(self.index[curr[0]][curr[1]])
                elif (level == 3):
                    self.low_priority.add(self.index[curr[0]][curr[1]])
                for d in directions:
                    x = curr[0] + d[0]
                    y = curr[1] + d[1]
                    if (self.validate_coord(x, y) and (x, y) not in seen):
                        seen.add((x, y))
                        queue.append((x, y))
            if (level < 3):
                level += 1

    def marginal_value(self, good):
        curr_alloc = set(self.goods_to_consider)
        curr_value = self.calc_total_valuation(curr_alloc)
        curr_alloc.discard(good)
        return abs(curr_value - self.calc_total_valuation(curr_alloc))
    
    def national_bidder_strategy(self): 
        # TODO: Fill out with your national bidder strategy
        min_bids = self.get_min_bids()
        valuations = self.get_valuations() 
        bids = {}
        if len(self.goods_to_consider) <= 6:
            # Rage quit
            return bids
        for g in min_bids:
            if (g in self.goods_to_consider):
                if (g in self.border):
                    if (min_bids[g] > self.BORDER_SHADE * self.marginal_value(g)):
                        self.goods_to_consider.discard(g)
                        continue
                else:
                    if (self.counter >= self.GRACE_PERIOD):
                        if (min_bids[g] > self.OUTER_SHADE * self.marginal_value(g)):
                            self.goods_to_consider.discard(g)
                            continue
                    else:
                        self.counter += 1
                bids[g] = min_bids[g]
        # for g in min_bids:
        #     if (g in self.goods_to_consider):
        #         if (g in self.border):
        #             if (min_bids[g] > self.BORDER_SHADE * self.marginal_value(g)):
        #                 self.goods_to_consider.discard(g)
        #                 continue
        #             bids[g] = self.BORDER_SHADE * self.marginal_value(g)
        #         else:
        #             if (self.counter >= self.GRACE_PERIOD):
        #                 if (min_bids[g] > self.OUTER_SHADE * self.marginal_value(g)):
        #                     self.goods_to_consider.discard(g)
        #                     continue
        #                 bids[g] = self.OUTER_SHADE * self.marginal_value(g)
        #             else:
        #                 self.counter += 1
        #                 bids[g] = min_bids[g]
        return bids

    def regional_bidder_strategy(self): 
        # TODO: Fill out with your regional bidder strategy
        min_bids = self.get_min_bids()
        valuations = self.get_valuations() 
        bids = {} 
        for g in self.goods_to_consider:
            shade = 1
            if (g in self.top_priority):
                shade = self.TOP_SHADE
            elif (g in self.high_priority):
                shade = self.HIGH_SHADE
            elif (g in self.mid_priority):
                shade = self.MID_SHADE
            elif (g in self.low_priority):
                shade = self.LOW_SHADE
            if (min_bids[g] > shade * self.marginal_value(g)):
                continue
            bids[g] = min_bids[g]
        return bids

    def get_bids(self):
        if self.is_national_bidder(): 
            return self.national_bidder_strategy()
        else: 
            if (len(self.top_priority) == 0):
                self.determine_priority(3)
            return self.regional_bidder_strategy()
    
    def update(self):
        #TODO: Fill out with anything you want to update each round
        pass 

################### SUBMISSION #####################
my_agent_submission = MyAgent(NAME)
####################################################


def process_saved_game(filepath): 
    """ 
    Here is some example code to load in a saved game in the format of a json.gz and to work with it
    """
    print(f"Processing: {filepath}")
    
    # NOTE: Data is a dictionary mapping 
    with gzip.open(filepath, 'rt', encoding='UTF-8') as f:
        game_data = json.load(f)
        for agent, agent_data in game_data.items(): 
            if agent_data['valuations'] is not None: 
                # agent is the name of the agent whose data is being processed 
                agent = agent 
                
                # bid_history is the bidding history of the agent as a list of maps from good to bid
                bid_history = agent_data['bid_history']
                
                # price_history is the price history of the agent as a list of maps from good to price
                price_history = agent_data['price_history']
                
                # util_history is the history of the agent's previous utilities 
                util_history = agent_data['util_history']
                
                # util_history is the history of the previous tentative winners of all goods as a list of maps from good to winner
                winner_history = agent_data['winner_history']
                
                # elo is the agent's elo as a string
                elo = agent_data['elo']
                
                # is_national_bidder is a boolean indicating whether or not the agent is a national bidder in this game 
                is_national_bidder = agent_data['is_national_bidder']
                
                # valuations is the valuations the agent recieved for each good as a map from good to valuation
                valuations = agent_data['valuations']
                
                # regional_good is the regional good assigned to the agent 
                # This is None in the case that the bidder is a national bidder 
                regional_good = agent_data['regional_good']
            
            # TODO: If you are planning on learning from previously saved games enter your code below. 
            
            
        
def process_saved_dir(dirpath): 
    """ 
     Here is some example code to load in all saved game in the format of a json.gz in a directory and to work with it
    """
    for filename in os.listdir(dirpath):
        if filename.endswith('.json.gz'):
            filepath = os.path.join(dirpath, filename)
            process_saved_game(filepath)
            

if __name__ == "__main__":
    
    # Heres an example of how to process a singular file 
    # process_saved_game(path_from_local_root("saved_games/2024-04-08_17-36-34.json.gz"))
    # or every file in a directory 
    # process_saved_dir(path_from_local_root("saved_games"))
    
    ### DO NOT TOUCH THIS #####
    agent = MyAgent(NAME)
    arena = LSVMArena(
        num_cycles_per_player = 1,
        timeout=1,
        local_save_path="saved_games",
        players=[
            agent,
            MyAgent("CP - MyAgent"),
            MyAgent("CP2 - MyAgent"),
            MyAgent("CP3 - MyAgent"),
            # MyAgent("CP4 - MyAgent"),
            # MyAgent("CP5 - MyAgent"),
            MinBidAgent("Min Bidder"), 
            JumpBidder("Jump Bidder"), 
            TruthfulBidder("Truthful Bidder"), 
        ]
    )
    
    start = time.time()
    arena.run()
    end = time.time()
    print(f"{end - start} Seconds Elapsed")
