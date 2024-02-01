import sys
from typing import Literal
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletionChunk
from dotenv import load_dotenv
import os
from helpers import tokens_counter

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Content:
    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path
        self.model: Literal["gpt-4-turbo-preview", "gpt-3.5-turbo"] = "gpt-3.5-turbo"

        with open(file_path, "r", encoding="utf-8") as file:
            self.content: str = file.read()

        replacers: dict[str, str] = {"\n\n": "\n", "\t": " ", "  ": " "}

        for bad, good in replacers.items():
            while bad in self.content:
                self.content = self.content.replace(bad, good)

        self.questions: list[str] = []
        self.content_tokens: int = tokens_counter.count_tokens(self.content, self.model)
        # self.questions_tokens: int = 0

    def change_model(
        self, model: Literal["gpt-4-turbo-preview", "gpt-3.5-turbo"]
    ) -> None:
        self.model = model
        self.content_tokens = tokens_counter.count_tokens(self.content, self.model)

    # def update_counters(self):
    #     self.questions_tokens = 0
    #     for q in self.questions:
    #         self.questions_tokens += tokens_counter.count_tokens(q, self.model)
    #     self.questions.tokens += 4 * len(self.questions)

    def make_a_question(
        self, n_alternatives: int, say_correct_answer: bool = False
    ) -> None:
        if not tokens_counter.do_you_want_to_continue(
            self.content_tokens, self.model, threshold=500
        ):
            return

        mode: str = (
            "Coloque um asterisco à esquerda da alternativa verdadeira."
            if say_correct_answer
            else "Não indique a alternativa verdadeira."
        )

        res: Stream[ChatCompletionChunk] = client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": f"Você é um gerador de quizzes com {n_alternatives} alternativas, sendo apenas uma a correta.",
                },
                {
                    "role": "system",
                    "name": "system_reader",
                    "content": "Observe o conteúdo: " + self.content,
                },
                {
                    "role": "system",
                    "name": "system_role",
                    "content": f"Crie uma pergunta sobre o conteúdo acima com {n_alternatives-1} alternativas falsas e uma alternativa verdadeira. Apresente apenas a pergunta e as alternativas. "
                    + mode,
                },
                {
                    "role": "system",
                    "content": "Use letras minúsculas para as alternativas. As alternativas devem ser únicas. Não repita as alternativas!",
                },
            ],
            stream=True,
        )

        final = ""
        for chunk in res:
            _aux = chunk.choices[0].delta.content or ""
            final += _aux
            sys.stdout.write(_aux)
            sys.stdout.flush()
        print()

        self.questions.append(final)
