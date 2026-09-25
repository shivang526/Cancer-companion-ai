import re

from typing import List

from utils.logger import logger


class QuestionOrganizerAgent:
    """Helps users prepare questions for their healthcare team."""

    def __init__(self):
        self.question_categories = {
            "treatment": "Questions about treatment options",
            "symptoms": "Questions about symptoms and side effects",
            "lifestyle": "Questions about daily life and activities",
            "follow_up": "Questions about next steps and monitoring",
        }

    # ============================================================
    # Detect language
    # ============================================================

    def is_hinglish(
        self,
        message: str,
    ) -> bool:
        """Detect common Roman Hindi / Hinglish expressions."""

        message_lower = message.lower()

        hinglish_words = [
            "mujhe",
            "mera",
            "meri",
            "mere",
            "mujhko",
            "doctor se",
            "kya",
            "kaise",
            "kyun",
            "kyu",
            "batao",
            "bata do",
            "samjhao",
            "samjao",
            "puchu",
            "poochu",
            "puchna",
            "poochna",
            "chahiye",
            "hai",
            "hota",
            "hoti",
            "raha",
            "rahi",
            "baare mein",
            "bare mein",
            "agla",
            "agli",
        ]

        return any(
            phrase in message_lower
            for phrase in hinglish_words
        )

    # ============================================================
    # Extract concerns
    # ============================================================

    def extract_concerns(
        self,
        user_message: str,
    ) -> List[str]:
        """Identify the topics the user wants to discuss."""

        concerns: List[str] = []

        message_lower = user_message.lower()

        patterns = {
            "treatment": (
                r"(treatment|therapy|medication|medicine|"
                r"chemo|chemotherapy|radiation|इलाज)"
            ),

            "symptoms": (
                r"(pain|tired|fatigue|nausea|sleep|appetite|"
                r"vomit|symptom|dard|thakan|ulti|matli)"
            ),

            "lifestyle": (
                r"(work|exercise|diet|food|family|daily|"
                r"routine|khana|exercise|kaam|roz)"
            ),

            "follow_up": (
                r"(next|follow|appointment|test|scan|results|"
                r"report|agla|agli|result|test)"
            ),
        }

        for category, pattern in patterns.items():

            if re.search(
                pattern,
                message_lower,
            ):
                concerns.append(category)

        logger.info(
            "QuestionOrganizerAgent: "
            f"Extracted concerns {concerns}"
        )

        return concerns

    # ============================================================
    # Generate questions
    # ============================================================

    def generate_questions(
        self,
        concerns: List[str],
        user_message: str = "",
    ) -> str:
        """Generate concise questions for the healthcare team."""

        hinglish = self.is_hinglish(user_message)

        # --------------------------------------------------------
        # English questions
        # --------------------------------------------------------

        english_templates = {
            "treatment": [
                "What is the main goal of this treatment?",
                "What side effects should I watch for?",
            ],

            "symptoms": [
                "Could this symptom be related to my condition or treatment?",
                "When should I contact my healthcare team about this symptom?",
            ],

            "lifestyle": [
                "What daily activities are safe for me right now?",
                "Are there any lifestyle or diet changes I should discuss with you?",
            ],

            "follow_up": [
                "What are the next steps in my care?",
                "When should I have my next appointment or test?",
            ],
        }

        # --------------------------------------------------------
        # Hinglish questions
        # --------------------------------------------------------

        hinglish_templates = {
            "treatment": [
                "Is treatment ka main goal kya hai?",
                "Is treatment ke kaunse side effects mujhe notice karne chahiye?",
            ],

            "symptoms": [
                "Kya ye symptom meri condition ya treatment se related ho sakta hai?",
                "Is symptom ke liye mujhe doctor se kab contact karna chahiye?",
            ],

            "lifestyle": [
                "Abhi main kaunsi daily activities safely kar sakta/sakti hoon?",
                "Kya mujhe diet ya lifestyle mein koi changes doctor se discuss karne chahiye?",
            ],

            "follow_up": [
                "Mere care ka next step kya hoga?",
                "Meri next appointment ya test kab hona chahiye?",
            ],
        }

        templates = (
            hinglish_templates
            if hinglish
            else english_templates
        )

        # --------------------------------------------------------
        # Generate questions
        # --------------------------------------------------------

        questions: List[str] = []

        for concern in concerns:

            if concern in templates:

                questions.extend(
                    templates[concern][:2]
                )

        # Remove duplicates
        questions = list(
            dict.fromkeys(questions)
        )

        # Keep response concise
        questions = questions[:4]

        # --------------------------------------------------------
        # No specific concern
        # --------------------------------------------------------

        if not questions:

            if hinglish:

                questions = [
                    "Meri condition ke baare mein mujhe sabse important kya samajhna chahiye?",
                    "Mere care ka next step kya hoga?",
                    "Agar mujhe koi concern ho to mujhe kisse contact karna chahiye?",
                ]

            else:

                questions = [
                    "What is the most important thing I should understand about my condition?",
                    "What are the next steps in my care?",
                    "Who should I contact if I have concerns?",
                ]

        # --------------------------------------------------------
        # Response
        # --------------------------------------------------------

        if hinglish:

            response_lines = [
                "Aap apni medical team se ye questions pooch sakte hain:",
                "",
            ]

        else:

            response_lines = [
                "You may want to ask your medical team:",
                "",
            ]

        for index, question in enumerate(
            questions,
            start=1,
        ):
            response_lines.append(
                f"{index}. {question}"
            )

        response_lines.append("")

        if hinglish:

            response_lines.append(
                "In questions ko appointment se pehle note kar lena helpful ho sakta hai."
            )

        else:

            response_lines.append(
                "It may help to write these questions down before your appointment."
            )

        response_lines.append("")
        response_lines.append(
            "⚠️ I am not a doctor and cannot provide medical advice. "
            "Please consult a qualified medical professional."
        )

        response = "\n".join(
            response_lines
        )

        logger.info(
            "QuestionOrganizerAgent: "
            f"Generated {len(questions)} questions"
        )

        return response