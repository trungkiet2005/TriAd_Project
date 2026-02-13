"""
Checker - Base class for hallucination detection.

Adapted from nicer_than_human's checker.py to match original paper format.
Uses LLM connector directly instead of through agent.
"""

import json
import warnings
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.checkers.checker_utils import find_json_object


class Checker:
    """
    Base class for hallucination checkers.
    
    Checkers ask questions to LLM agents about the game state
    and verify if their answers are correct, helping detect
    hallucinations and understanding errors.
    """

    def __init__(self, checker_name: str, questions: List[str], questions_labels: List[str]):
        """
        Initialize the Checker.

        Args:
            checker_name (str): Name of this checker.
            questions (List[str]): List of question templates.
            questions_labels (List[str]): Labels for each question type.
        """
        self.name = checker_name

        # String constants (matching original)
        self.checker_str = "checker"
        self.question_str = "question"
        self.sample_mean_str = "sample_mean"
        self.sample_variance_str = "sample_variance"
        self.total_str = "total"
        self.positives_str = "positives"
        self.squared_diffs_sum_str = "squared_diffs_sum"
        self.prompt_str = "prompt"
        self.generated_text_str = "generated_text"
        self.answer_str = "answer"

        self.questions = questions
        self.questions_labels = questions_labels
        self.questions_results: Dict[str, Dict] = {}
        
        # Initialize results structure for each question
        for label in self.questions_labels:
            question = self.questions[self.questions_labels.index(label)]
            self.questions_results[label] = {
                self.checker_str: checker_name,
                self.question_str: question,
                self.sample_mean_str: 0,
                self.sample_variance_str: 0,
                self.total_str: 0,
                self.positives_str: 0,
                self.squared_diffs_sum_str: 0,
                self.prompt_str: [],
                self.generated_text_str: [],
                self.answer_str: [],
            }
        
        # Aggregate statistics
        self.sample_mean = 0
        self.sample_variance = 0
        self.total = 0
        self.positives = 0
        self.squared_diffs_sum = 0
        self.system_prompt = None
        
        # LLM connector (set via set_llm_connector)
        self.llm_connector = None
        
        # Agent and round context tracking (for CSV export)
        self._current_agent: str = ""
        self._current_round: int = 0

        # Configuration
        self.max_new_tokens = 128
        self.temperature = 0.7

    def get_name(self) -> str:
        """Get the checker name."""
        return self.name

    def set_llm_connector(self, connector) -> None:
        """
        Set the LLM connector for asking questions.

        This should be a connector with send_prompt(prompt, max_tokens) method.
        """
        self.llm_connector = connector

    def set_current_agent(self, agent_name: str) -> None:
        """Set the current agent being queried (for result tracking in CSV)."""
        self._current_agent = agent_name

    def set_current_round(self, round_number: int) -> None:
        """Set the current round number (for result tracking in CSV)."""
        self._current_round = round_number

    def get_answer_from_llm(self, prompt: str, label: str, max_new_tokens: int = None, 
                            temperature: float = None, need_str: bool = True) -> Any:
        """
        Get an answer from the LLM model given a prompt.

        Args:
            prompt (str): The prompt to send.
            label (str): Label for categorizing this Q&A.
            max_new_tokens (int): Max tokens for response.
            temperature (float): LLM temperature.
            need_str (bool): Whether to convert answer to string.

        Returns:
            The answer from the LLM (string if need_str=True).
        """
        if max_new_tokens is None:
            max_new_tokens = self.max_new_tokens
        
        self.questions_results[label][self.prompt_str].append(prompt)
        
        # Retry loop
        max_retries = 1
        generated_text = ""
        json_object = None
        
        for attempt in range(max_retries):
            # Use the LLM connector directly
            try:
                generated_text = self.llm_connector.send_prompt(prompt, max_tokens=max_new_tokens)
            except TypeError:
                # Fallback if connector doesn't support max_tokens
                generated_text = self.llm_connector.send_prompt(prompt)
            
            self.questions_results[label][self.generated_text_str].append(generated_text)
            
            # Try to parse JSON from response
            json_object = find_json_object(generated_text)
            
            if json_object is not None:
                break
                
            # If failed, print warning and retry
            preview = str(generated_text)[:100] if generated_text else "None"
            if attempt < max_retries - 1:
                print(f"[Checker:{self.name}] WARNING: No JSON found (Attempt {attempt+1}/{max_retries}). Retrying...")
        
        if json_object is not None:
            try:
                # Print full JSON for debugging
                print(f"[Checker:{self.name}] JSON Response: {json.dumps(json_object, ensure_ascii=False)}")
                answer = json_object.get("answer", generated_text)
            except Exception as e:
                warnings.warn(f"Error {str(e)}. No key 'answer' in JSON: {json_object}. Returning entire generated text.")
                answer = generated_text
        else:
            preview = str(generated_text)[:100] if generated_text else "None"
            warnings.warn(f"Could not find a valid JSON object in the generated text: {preview}...")
            answer = generated_text if generated_text else ""
        
        if need_str:
            answer = str(answer)
        return answer

    def check_answer(self, llm_answer: Any, correct_answer: Any, label: str) -> bool:
        """
        Check if the LLM answer is correct.

        Args:
            llm_answer: The answer from the LLM.
            correct_answer: The expected correct answer.
            label: The question label.

        Returns:
            bool: True if the answer is correct.
        """
        is_set = isinstance(correct_answer, set)
        is_list = isinstance(correct_answer, list)
        correct = False
        
        if is_set or is_list:
            if llm_answer is None:
                correct = False
            elif len(llm_answer) == len(correct_answer):
                correct = True
                if is_list:
                    for i in range(len(llm_answer)):
                        if isinstance(llm_answer[i], str) and isinstance(correct_answer[i], str):
                            if llm_answer[i].casefold() != correct_answer[i].casefold():
                                correct = False
                                break
                        elif llm_answer[i] != correct_answer[i]:
                            correct = False
                            break
                else:
                    insensitive_set = {c.casefold() if isinstance(c, str) else c for c in correct_answer}
                    for llm_ans in llm_answer:
                        ans_to_check = llm_ans.casefold() if isinstance(llm_ans, str) else llm_ans
                        if ans_to_check not in insensitive_set:
                            correct = False
                            break
        else:
            if llm_answer is None:
                correct = False
            elif isinstance(llm_answer, str) and isinstance(correct_answer, str):
                correct = llm_answer.casefold() == correct_answer.casefold()
            else:
                correct = str(llm_answer) == str(correct_answer)
        
        self.questions_results[label][self.answer_str].append({
            "correct_answer": str(correct_answer),
            "llm_answer": str(llm_answer),
            "is_correct": correct,
            "agent_name": self._current_agent,
            "round_number": self._current_round
        })
        
        self.update_aggregates_for_question(label, int(correct))
        self.update_aggregates_for_checker(correct)
        return correct

    def update_aggregates_for_question(self, label: str, answer: int) -> None:
        """Update statistics for a specific question."""
        self.questions_results[label][self.positives_str] += answer
        positives = self.questions_results[label][self.positives_str]
        self.questions_results[label][self.total_str] += 1
        total = self.questions_results[label][self.total_str]
        sample_mean = positives / total if total > 0 else 0
        self.questions_results[label][self.sample_mean_str] = sample_mean
        
        self.questions_results[label][self.squared_diffs_sum_str] += ((answer - sample_mean) ** 2)
        squared_diffs_sum = self.questions_results[label][self.squared_diffs_sum_str]
        sample_variance = squared_diffs_sum / (total - 1) if total > 1 else 0
        self.questions_results[label][self.sample_variance_str] = sample_variance

    def update_aggregates_for_checker(self, answer: bool) -> None:
        """Update aggregate statistics for the checker."""
        self.positives += int(answer)
        self.total += 1
        self.sample_mean = self.positives / self.total if self.total > 0 else 0
        self.squared_diffs_sum += ((int(answer) - self.sample_mean) ** 2)
        self.sample_variance = self.squared_diffs_sum / (self.total - 1) if self.total > 1 else 0

    def ask_checker_questions(self, game, player_name: str = "", history_window_size: int = None) -> None:
        """
        Ask all checker questions for the current game state.
        To be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement ask_checker_questions")

    def save_results(self, out_dir: Path, infix: str = None) -> None:
        """Save checker results to a JSON file."""
        results = {
            self.name: {
                self.checker_str: self.name,
                self.sample_mean_str: self.sample_mean,
                self.sample_variance_str: self.sample_variance,
                self.total_str: self.total,
                self.positives_str: self.positives,
            }
        }
        
        for label in self.questions_results:
            results[label] = {
                self.checker_str: self.name,
                self.question_str: self.questions_results[label][self.question_str],
                self.sample_mean_str: self.questions_results[label][self.sample_mean_str],
                self.sample_variance_str: self.questions_results[label][self.sample_variance_str],
                self.total_str: self.questions_results[label][self.total_str],
                self.positives_str: self.questions_results[label][self.positives_str],
            }
        
        json_results = json.dumps(results, indent=4)
        out_dir = out_dir / self.name
        out_dir.mkdir(exist_ok=True, parents=True)
        
        filename = f"{self.name}.json" if infix is None else f"{self.name}_{infix}.json"
        with open(out_dir / filename, "w") as out_file:
            out_file.write(json_results)

    def save_complete_answers(self, out_dir: Path, infix: str = None) -> None:
        """Save complete answers including prompts and generated text (matching nicer_than_human format)."""
        complete_answers = {}
        for label in self.questions_results:
            complete_answers[label] = {}
            question = self.questions_results[label][self.question_str]
            for idx in range(len(self.questions_results[label][self.prompt_str])):
                complete_answers[label][idx] = {
                    self.question_str: question,
                    self.prompt_str: self.questions_results[label][self.prompt_str][idx],
                    self.generated_text_str: self.questions_results[label][self.generated_text_str][idx],
                    self.answer_str: self.questions_results[label][self.answer_str][idx],
                }
        
        # Save complete answers
        json_complete_answers = json.dumps(complete_answers, indent=4)
        complete_answers_out_dir = out_dir / self.name / "complete_answers"
        complete_answers_out_dir.mkdir(exist_ok=True, parents=True)
        
        if infix is None:
            tmp_out_file_name = complete_answers_out_dir / "complete_answers.json"
        else:
            tmp_out_file_name = complete_answers_out_dir / f"complete_answers_{infix}.json"
        with open(tmp_out_file_name, "w") as out_file:
            out_file.write(json_complete_answers)
        
        # Save light answers (only is_correct boolean per question)
        light_complete_answers = {}
        for label in complete_answers.keys():
            light_single_complete_answer = {
                "question": complete_answers[label][0][self.question_str] if 0 in complete_answers[label] else "",
                "answers": []
            }
            for iteration in complete_answers[label].keys():
                light_single_complete_answer["answers"].append(
                    complete_answers[label][iteration][self.answer_str]["is_correct"]
                )
            light_complete_answers[label] = light_single_complete_answer
        
        light_answers_out_dir = out_dir / self.name / "light_answers"
        light_answers_out_dir.mkdir(exist_ok=True, parents=True)
        
        if infix is None:
            light_complete_answers_file = light_answers_out_dir / "light_answers.json"
        else:
            light_complete_answers_file = light_answers_out_dir / f"light_answers_{infix}.json"
        with open(light_complete_answers_file, "w") as f:
            json.dump(light_complete_answers, f, indent=4)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of checker results."""
        return {
            "checker": self.name,
            "total_questions": self.total,
            "correct_answers": self.positives,
            "accuracy": round(self.sample_mean, 4) if self.total > 0 else 0,
            "variance": round(self.sample_variance, 4) if self.total > 1 else 0
        }

    def get_detailed_results(self) -> Dict[str, Any]:
        """Get detailed results for all questions."""
        results = {}
        for label, data in self.questions_results.items():
            results[label] = {
                "question": data[self.question_str],
                "total": data[self.total_str],
                "correct": data[self.positives_str],
                "accuracy": data[self.sample_mean_str],
                "answers": data[self.answer_str][-5:]  # Last 5 answers
            }
        return results

