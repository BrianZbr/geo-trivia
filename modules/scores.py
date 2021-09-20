import os
import pickle


class Scores:
    def __init__(self, game) -> None:
        self.username = game.username
        self.score = game.score
        self.region = game.region
        self.topic = game.TOPIC_NAMES[game.categories]
        # scores are tracked seperately for each combination of region and topic category
        self.game_pair = (game.region, game.categories)
        self.complete_records = self.set_raw_score_records()
        self.personal_best, self.record_holder, self.record_high = self.set_top_records()
        self.update_records()

    def set_raw_score_records(self):
        if os.path.exists("scores.pkl"):
            # attempt to read the file for past records
            return pickle.load(open("scores.pkl", "rb"))
        else:
            return {}

    def set_top_records(self):
        '''Returns a dictionary with only two keys, the current username and the record-holders username. Values are the highest record scores for each of these two users. '''
        if not self.complete_records == {}:
            if "all_users" in self.complete_records.keys():
                # Check for highest score of any user in this game_pair category. Underscores are not allowed in usernames in order to protect the special key, all_users
                if self.game_pair in self.complete_records["all_users"].keys():
                    record_high = self.complete_records["all_users"][self.game_pair][0]
                    record_holder = self.complete_records["all_users"][self.game_pair][1]
                else:
                    record_high = None
                    record_holder = None
            else:
                record_high = None
            if self.username in self.complete_records.keys():
                # check for highest score of the current user in present game_pair
                if self.game_pair in self.complete_records[self.username].keys():
                    user_high = self.complete_records[self.username][self.game_pair]
                else:
                    user_high = None
            else:
                user_high = None
        return (user_high, record_holder, record_high)

    def report_results(self):
        '''Displays a summary of how the current game compares with previous score records.'''
        print(
            f"\nYou scored {self.score} points this round, playing the {self.region} region and {self.topic} category.")
        if self.personal_best:
            if self.score > self.personal_best:
                print(
                    f"You beat your previous high score of {self.personal_best} points for this region and topic!")
            elif self.score == self.personal_best:
                print(
                    f"You matched your previous high score of {self.personal_best} points for this region and topic.")
            else:
                print(
                    f"Your high score for this region and topic is {self.personal_best}.")
        else:
            print(
                f"This is your first time playing this region and category'.")
        if self.record_high:
            if self.score > self.record_high:
                if self.record_holder != self.username:
                    print(
                        f"You beat {self.record_holder}'s high score of {self.record_high}!")
                else:
                    print("You remain the record holder!")
            else:
                if self.record_holder != self.username:
                    print(
                        f"The record score of {self.record_high} is held by {self.record_holder}")
                else:
                    print(
                        f"You hold the record score of {self.record_high} points.")

    def update_records(self):
        '''Add the results of the current game to the data file if a record was broken.'''
        if self.personal_best:
            # user has played this region and topic before
            if self.score > self.personal_best:
                self.complete_records[self.username][self.game_pair] = self.score
        else:
            # user has not played this region and topic before
            self.complete_records[self.username] = {}
            self.complete_records[self.username][self.game_pair] = self.score
        if self.record_high:
            if self.score > self.record_high:
                self.complete_records["all_users"][self.game_pair] = (
                    self.score, self.username)
        else:
            if "all_users" in self.complete_records.keys():
                self.complete_records["all_users"][self.game_pair] = (
                    self.score, self.username)
            else:
                self.complete_records["all_users"] = {}
                self.complete_records["all_users"][self.game_pair] = (
                    self.score, self.username)
        with open('scores.pkl', 'wb') as f:
            # update the data file
            pickle.dump(self.complete_records, f)
