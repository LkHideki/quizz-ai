from helpers.question_maker import Content


historia = Content("data/content.txt")
historia.change_model("gpt-4-turbo-preview")
historia.make_a_question(5)
