import random


class Question:
    '''Takes a game object as input. Once main properties have been set, the "ask" method poses the question and gets the user's input '''

    def __init__(self, game) -> None:
        self.game = game
        self.number = self.game.question_counter
        if type(self.game.categories) == tuple:
            self.category = random.choice(self.game.categories)
        else:
            self.category = self.game.categories
        self.format = self.set_format()
        # "get" because it returns values for wrong_choices to
        self.answer_pair = self.get_answer_pair()
        self.question_text = self.set_question_text()
        self.correct_choice = self.set_correct_choice()
        self.wrong_choices = self.set_wrong_choices()
        self.user_choice = None
        self.answered_correctly = None
        self.feedback = None

    def format_item_list(self, items):
        '''Takes a list and returns a string formatted for printing.'''
        if len(items) == 1:
            return items[0].strip()
        elif len(items) == 2:
            return items[0].strip() + " and " + items[1].strip()
        else:
            comma_list = ""
            for item in items[:-1]:
                comma_list = comma_list+(item.strip()+", ")
            comma_list = comma_list + "and " + items[-1].strip()
            return comma_list

    def set_format(self) -> tuple:
        '''Randomly selects an appropriate question format based on self.category. Returns a tuple where the first string what will be stated in the question text, and the second string represents what the multiple choice options will be.'''
        if random.getrandbits(1) == 0:
            return(('country', self.category))
        else:
            return((self.category, 'country'))

    def get_answer_pair(self) -> dict:
        '''Returns a dict with a random country from the appropriate region, and a corresponding item of the appropriate category, which can be the basis for a question. Used countries and items are excluded.'''
        while True:
            country = random.choice(
                list(self.game.data.countries['major region'][self.game.region]))
            if country in self.game.used['countries']:
                continue
            if not country in self.game.data.items[self.category].keys():
                # Ensures that the chosen country has appropriate item data available
                continue
            item = random.choice(
                self.game.data.items[self.category][country])
            if item in self.game.used['items']:
                continue
            break
        answer_pair = {
            'country': country,
            'item': item
        }
        return answer_pair

    def set_question_text(self) -> str:
        '''Create the f-string of the question text based on self.answer_pair'''
        if self.format == ("country", "capital"):
            return f"What is the capital of {self.answer_pair['country']}?"
        elif self.format == ("capital", "country"):
            return f"{self.answer_pair['item']} is the capital of which country?"
        elif self.format == ("country", "languages"):
            return f"Which language is more commonly spoken in {self.answer_pair['country']}?"
        elif self.format == ("languages", "country"):
            return f"{self.answer_pair['item']} is a language most commonly spoken in which country?"
        elif self.format == ("country", "dishes"):
            return f"Which food is considered a typical dish in {self.answer_pair['country']}?"
        elif self.format == ("dishes", "country"):
            return f"{self.answer_pair['item']} is a dish most typical of which country?"
        else:
            print("unrecognized question type!!!", self.format)
            return False

    def set_correct_choice(self) -> tuple:
        '''Assigns a random letter to the correct answer choice. Returns a 2-tuple with the letter and the answer.'''
        if self.format[1] == "country":
            return (random.choice(self.game.LETTERS), self.answer_pair['country'])
        else:
            return (random.choice(self.game.LETTERS), self.answer_pair['item'])

    def set_wrong_choices(self) -> dict:
        '''Assigns appropriate but incorrect answer choices to all the letter options, except the one which is assigned to the correct answer. Returns a dictionary, where the assigned letter options are the keys, and the values are the choices themselves.'''
        used_countries = []
        used_items = []
        wrong_choices = {}
        for letter in self.game.LETTERS:
            if not letter == self.correct_choice[0]:
                while True:
                    candidate_pair = self.get_answer_pair()
                    candidate_country = candidate_pair['country']
                    candidate_item = candidate_pair['item']
                    if candidate_country == self.answer_pair['country']:
                        continue
                    if candidate_country in used_countries:
                        continue
                    for item in self.game.data.items[self.category][candidate_country]:
                        item_problem = False
                        # ensure the correct country and the wrong answer's candidate country don't share any relevant items in common.
                        if item in self.game.data.items[self.category][self.answer_pair['country']]:
                            item_problem = True
                            break
                    if item_problem:
                        continue
                    if candidate_item in used_items:
                        continue
                    break
                if self.format[1] == "country":
                    wrong_choices[letter] = candidate_country
                else:
                    wrong_choices[letter] = candidate_item
                used_countries.append(candidate_country)
                used_items.append(candidate_item)
        return wrong_choices

    def ask(self, testing=False):
        '''Displays the question and answer choices, then gets user input. Updates self.answered_correctly to True or False'''
        print("\n========================")
        print("Question", self.number, ":")
        print(self.question_text+"\n")
        for letter in self.game.LETTERS:
            # display the options
            if letter == self.correct_choice[0]:
                print(letter+":", self.correct_choice[1])
            else:
                print(letter+":", self.wrong_choices[letter])
        while True:
            # get user answer
            if testing:
                self.user_choice = random.choice(self.game.LETTERS)
            else:
                self.user_choice = input("\nYour answer? ").upper()
            if not self.user_choice in self.game.LETTERS:
                print("Invalid input, try again!")
                print("")
            else:
                break
        # update status and return
        if self.user_choice.upper() == self.correct_choice[0]:
            print("\nCorrect, you gain a point!\n")
            self.answered_correctly = True
            self.feedback = Feedback(self)
        else:
            print("\nIncorrect!")
            self.answered_correctly = False
            self.feedback = Feedback(self)
            self.feedback.print_looking_for()

    def set_feedback(self):
        '''Sets appropriate feedback based on user's result.'''
        country = self.answer_pair['country']
        item = self.answer_pair['item']
        raw_countries_list = self.game.data.countries[self.category][item]
        raw_items_list = self.game.data.items[self.category][country]
        countries = self.format_item_list(raw_countries_list)
        items = self.format_item_list(raw_items_list)
        if self.category == "capital":
            self.feedback = f"{items} is the capital of {country}.\n"
        elif self.category == "languages":
            self.feedback = f"The major languages spoken in {country} are: {items}\n"
        elif self.category == "dishes":
            if len(raw_items_list) > 1:
                self.feedback = f"The typical national dishes of {country} include: {items}\n"
            else:
                self. feedback = f"The national dish of {country} is {item}."
        else:
            self.feedback = "Category not implemented! " + self.category
        if self.answered_correctly:
            if len(raw_items_list) > 1:
                if self.format[1] == "country":
                    self.feedback += f"\nYour answer {self.answer_pair['country']} was correct."
                else:
                    self.feedback += f"\nYour answer {self.answer_pair['item']} was correct."
        else:
            # If user answered incorrectly, feedback statement requires further customization.
            if self.format[1] == "country":
                looking_for_statement = f"The answer we were looking for was {self.answer_pair['country']}.\n"
            else:
                looking_for_statement = f"The answer we were looking for was {self.answer_pair['item']}.\n"
            wrong_item_statement = f"\n\nYou said {self.wrong_choices[self.user_choice]}"
            if self.format == ("country", "capital"):
                self.feedback = f"The capital of {country} is {items}." + \
                    wrong_item_statement
            elif self.format == ("capital", "country"):
                self.feedback += wrong_item_statement
            elif self.format == ("country", "languages"):
                self.feedback += wrong_item_statement + looking_for_statement
            elif self.format == ("languages", "country"):
                self.feedback = looking_for_statement + wrong_item_statement + \
                    f"\n{self.answer_pair['item']} is most commonly spoken in: {countries}"
            elif self.format == ("country", "dishes"):
                self.feedback = looking_for_statement + wrong_item_statement + self.feedback
            elif self.format == ("dishes", "country"):
                self.feedback = looking_for_statement + wrong_item_statement + \
                    f"\n{self.answer_pair['item']} is considered a national dish in: {countries}"
        return


class Feedback():
    def __init__(self, question) -> None:
        self.q = question
        self.game = self.q.game
        self.correct_items_statement = self.set_correct_items_statement()
        self.you_said = self.set_you_said()
        self.looking_for = self.set_looking_for()
        if not self.q.answered_correctly:
            self.wrong_item_statement = self.set_wrong_item_statement()

    def set_you_said(self):
        if self.q.answered_correctly:
            return f"You said {self.q.correct_choice[1]}"
        else:
            return f"You said {self.q.wrong_choices[self.q.user_choice]}"

    def set_looking_for(self):
        if self.q.format[1] == "country":
            return f"\nThe answer we were looking for was {self.q.answer_pair['country']}."
        else:
            return f"\nThe answer we were looking for was {self.q.answer_pair['item']}."

    def set_correct_items_statement(self):
        country = self.q.answer_pair['country']
        raw_items_list = self.q.game.data.items[self.q.category][country]
        items = self.q.format_item_list(raw_items_list)
        if self.q.category == "capital":
            return f"{items} is the capital of {country}."
        elif self.q.category == "languages":
            return f"The major languages spoken in {country} are: {items}"
        elif self.q.category == "dishes":
            if len(raw_items_list) > 1:
                return f"The typical national dishes of {country} include: {items}"
            else:
                return f"The national dish of {country} is {items}."
        else:
            return "Category not implemented! " + self.game.category

    def set_wrong_item_statement(self):
        return f"You said {self.q.wrong_choices[self.q.user_choice]}"

    def print_looking_for(self):
        if not self.q.answered_correctly:
            print(self.looking_for)

    def print_end_report(self):
        if self.q.answered_correctly:
            print(self.correct_items_statement)
        else:
            print(self.wrong_item_statement)
            print(self.looking_for)
            print(self.correct_items_statement)
