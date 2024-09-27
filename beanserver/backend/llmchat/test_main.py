# ruff: noqa

# import json
# import os
# from enum import Enum

# from groq import Groq
from prompt_toolkit import prompt

# from pydantic import BaseModel


# def ask_income_subcategories(category_name, subcategories):
#     # Function to ask for income subcategories
#     print(f"\nYou indicated that you have income from {
#           category_name}. Let's break that down:")
#     income_details = {}
#     for subcategory in subcategories:
#         while True:
#             income = prompt(f"How much do you earn from {
#                             subcategory}? (this should be some kind of time frequency input, like a calendar scheduler) $").strip()
#             try:
#                 # Try to convert the input to a float
#                 income_details[subcategory] = float(income)
#                 break
#             except ValueError:
#                 print(f"Invalid input for {
#                       subcategory}, please enter a numeric value.")
#     return income_details


# def ask_category_with_subcategories(category_name, subcategories):
#     # Template function to ask about high-level categories and their subcategories
#     has_income = ask_yes_no(f"Do you earn income from {category_name}?")

#     if has_income:
#         income_details = ask_income_subcategories(category_name, subcategories)
#         return income_details
#     return None


# def ask_yes_no(question):
#     # Function to ask yes/no questions and return a boolean
#     while True:
#         answer = prompt(f"{question} (yes/no): ").strip().lower()
#         if answer in ["yes", "y"]:
#             return True
#         if answer in ["no", "n"]:
#             return False
#         print("Please answer 'yes' or 'no'.")


# def gather_financial_info():
#     income_categories: dict = {
#         "Employment-Based Income": [
#             "Full-time Job",
#             "Part-time Job",
#             "Consulting",
#             "Freelancing",
#             "Gig Economy(could include delivery driving, ride-sharing, etc.)",
#             "Tutoring",
#             "Teaching",
#         ],
#         "Entrepreneurial/Business Income": [
#             "Entrepreneurship",
#             "Franchising",
#             "Online Business(e-commerce, digital products)",
#             "App Development",
#             "Software Sales",
#             "Handmade Goods(crafts, etc.)",
#             "Content Creation(YouTube, blogging, etc.)",
#             "Affiliate Marketing",
#             "Peer-to-Peer Lending",
#         ],
#         "Investment Income": [
#             "Stocks",
#             "Bonds",
#             "Mutual Funds",
#             "Dividend Stocks",
#             "Cryptocurrency",
#             "Real Estate(flipping properties or holding for appreciation or rent)",
#         ],
#         "Passive/Alternative Income": [
#             "Grants and Scholarships",
#             "Pensions",
#             "Social Security",
#             "Alimony/Child Support",
#             "Lottery Winnings",
#             "Inheritance",
#             "Crowdfunding",
#         ],
#         "Savings": ["Savings"],
#     }

#     income_tree = {}
#     for category, sub_category in income_categories.items():
#         income_for_cat = ask_category_with_subcategories(category, sub_category)
#         if income_for_cat is not None:
#             income_tree[category] = income_for_cat

#     return income_tree


# if __name__ == "__main__":
#     income_tree = gather_financial_info()
#     import json

#     print(json.dumps(income_tree, indent=4))

#     print("Now we do the same for expenses...")


# def main():
#     print(json.dumps(IncomeTree.model_json_schema(), indent=2))
#     print(json.dumps(Question.model_json_schema(), indent=2))


# class IncomeTree(BaseModel):
#     name: str
#     income: int | list["IncomeTree"]


# class QuestionType(str, Enum):
#     yes_no = "yes_no"
#     text_input = "text_input"


# class Question():
#     question: str
#     type: QuestionType


# class IncomeTreeUpdate:
#     parent_name: str
#     new_node: IncomeTree


# class LLMResponse(BaseModel):
#     client_question: Optional[Question]
#     server_update: Optional[IncomeTreeUpdate]


# def chat():
#     client = Groq(
#         api_key=os.environ.get("GROQ_API_KEY"),
#     )

#     chat_completion = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "system",
#                 "content": (
#                     "You are an AI assistant integrated into a budgeting and "
#                     "expense tracking application. Your role is to conduct a "
#                     "personalized Q&A session with users to help them "
#                     "determine what their income is."
#                     # Pass the json schema to the model. Pretty printing improves results.
#                     # f" The JSON object must use the schema: {
#                     #     json.dumps(Recipe.model_json_schema(), indent=2)}"
#                 )
#             },            {
#                 "role": "user",
#                 "content": f"Fetch a recipe for",
#             },
#         ],
#         model="llama3-8b-8192",
#         temperature=0,
#         # Streaming is not supported in JSON mode
#         stream=False,
#         # Enable JSON mode by setting the response format
#         response_format={"type": "json_object"})
#     print(chat_completion.choices[0].message.content)
