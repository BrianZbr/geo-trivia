from modules.data import Data
from modules.question import Question
from modules.scores import Scores


class Game:
    '''Plays a round a of trivia.'''
    TESTING = False     # If TESTING, answers will be automatically answered at random, with user choices determined by TEST_VALUES
    TEST_VALUES = ("Test User", "World",
                   ('capital', 'languages', 'dishes'))
    QUESTION_LIMIT = 10     # how many questions to ask per game
    LETTERS = ("A", "B", "C", "D")  # choices given to user for each question
    HOLD_FEEDBACK = True    # If True, hold detailed feedback to end of game
    QUESTION_FORMATS = {
        # These are the different topics the user can play. The keywords in the tuples represent dictionary keys in game.data.countries and game.data.items
        'All Topics': ('capital', 'languages', 'dishes'),
        'Capital Cities': ('capital'),
        'Languages': ('languages'),
        'National Dishes': ('dishes')
    }
    # same dictionary in reverse for score reporting
    TOPIC_NAMES = dict(zip(QUESTION_FORMATS.values(), QUESTION_FORMATS.keys()))

    def __init__(self, data):
        self.keep_playing = True  # if False, program will exit
        self.data = data   # The data object that questions are generated from
        self.username = None
        self.region = None
        self.categories = None
        self.score = 0
        self.question_counter = 1
        self.used = {
            # Primary purpose of this variable is for tracking what's been asked, in order to avoid repeating questions in the same game. It's also a convenient place to put problematic data items until these can be fixed.
            'countries': ["Luxembourg"],
            'items': ["", " ", "English", "its Thai name)", "S"]
        }
        self.questions = []

    def option_menu(self, options):
        '''Takes a list of options, prints them as a menu and returns the option selected by the user.'''
        # print options as a numbered list
        for place in range(1, len(options)+1):
            item = options[place-1]
            print(str(place)+':', item)
        # get response and return string
        print("")
        while True:
            answer = input("Your choice? ")
            if not answer.isdigit() or int(answer) > len(options) or int(answer) < 1:
                print("Please enter a valid digit.")
            else:
                return options[int(answer)-1]

    def start_game(self):
        '''Guides user through the initial decisions that must be set before asking questions.'''
        print("\nWorld Geography Trivia Game \n")
        # TODO enter name for previous user by default
        if self.TESTING:
            self.username, self.region, self.categories = self.TEST_VALUES
        else:
            while True:
                self.username = input("Who's playing [type your name]? \n")
                if not "_" in self.username:
                    break
                else:
                    print("Underscores are not allowed in usernames")
            while True:
                print("Choose the region you will play. \n")
                self.region = self.option_menu(
                    list(self.data.countries['major region'].keys()))
                # ask to choose QUESTION TOPIC
                print("Choose the topics you will play. \n")
                self.categories = self.QUESTION_FORMATS[self.option_menu(
                    list(self.QUESTION_FORMATS.keys()))]
                if self.region == "Oceania" and self.categories == "dishes":
                    print(
                        f"Sorry, insufficient data available to play {self.categories} for the region {self.region}. Please make a different selection.")
                else:
                    break
        return self.username, self.region, self.categories

    def final_report(self):
        correct = []
        incorrect = []
        for q in self.questions:
            if q.answered_correctly:
                correct.append(q)
            else:
                incorrect.append(q)
        print(f"\nYou answered {len(correct)} questions correctly.\n")
        for q in correct:
            print(f"\nQuestion {q.number}:")
            print(q.feedback.correct_items_statement)
            # TODO make this test more robust
            if "," in q.feedback.correct_items_statement:
                print(q.feedback.you_said)
        input("\nPress Enter to review incorrect answers\n")
        print(f"You answered {len(incorrect)} questions incorrectly.")
        for q in incorrect:
            print(f"\nQuestion {q.number}:")
            print(q.feedback.looking_for)
            print(q.feedback.correct_items_statement)
            print(q.feedback.you_said)


def main():
    '''Play rounds of trivia repeatedly until user exits.'''
    data = Data()
    new_game = True
    reuse_settings = False
    while True:
        if new_game:
            game = Game(data)
            game.start_game()
            new_game = False
        elif reuse_settings:
            game.__init__(data)
            game.score = 0
            game.question_counter = 1
            game.username, game.region, game.categories = reuse_settings
        while game.question_counter <= game.QUESTION_LIMIT:
            question = Question(game)
            question.ask(game.TESTING)
            if question.answered_correctly:
                game.score += 1
            game.used['countries'].append(question.answer_pair['country'])
            game.used['items'].append(question.answer_pair['item'])
            game.questions.append(question)
            game.question_counter += 1
        if game.HOLD_FEEDBACK:
            # TODO show immediate question feedback if not HOLD_FEEDBACK
            report_choice = input(
                "\nSee detailed report? Enter S to skip, anything else to continue: ")
            if report_choice.lower() != "s":
                game.final_report()
        input("Press Enter to see score report")
        scores = Scores(game)
        scores.report_results()
        scores.update_records()
        while True:
            end_choice = input(
                "\nPlay again as [s]ame user and settings, [d]ifferent user / settings, or [q]uit game? ")
            if end_choice.lower() == "s":
                new_game = False
                reuse_settings = (game.username, game.region, game.categories)
                break
            elif end_choice.lower() == "d":
                new_game = True
                break
            elif end_choice.lower() == "q":
                game.keep_playing = False
            if not game.keep_playing:
                break
        if not game.keep_playing:
            break


if __name__ == "__main__":
    main()
