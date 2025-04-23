import re
import json

def parse_formatted_philiri_text(text):
    title_splits = re.split(r'(?=TITLE:)', text)

    passage_pattern = r'TITLE:\s*(.*?)\s*\n\s*PASSAGE:\s*(.*?)\s*\n\s*QUESTIONS:(.*?)(?=\n\s*TITLE:|\Z)'
    passage_matches = re.findall(passage_pattern, text, re.DOTALL)

    all_passage_data = []
    all_question_data = []
    all_complete_data = []

    for i, section in enumerate(title_splits):
        if "TITLE:" not in section:
            continue
            
        try:
            # Extract title, passage, and questions from each section
            title_match = re.search(r'TITLE:\s*(.*?)\s*\n', section)
            passage_match = re.search(r'PASSAGE:\s*(.*?)\s*\n\s*QUESTIONS:', section, re.DOTALL)
            questions_match = re.search(r'QUESTIONS:(.*?)$', section, re.DOTALL)
            
            if not (title_match and passage_match and questions_match):
                continue
                
            title = title_match.group(1).strip()
            passage = passage_match.group(1).strip()
            questions_text = questions_match.group(1).strip()
            word_count = str(len(passage.split()))
            
            # Rest of your question parsing code remains the same...
            questions = []
            question_blocks = re.split(r'\n(?=\d+\.\s+)', questions_text)

            questions = []
            for block in question_blocks:
                match = re.match(r'(\d+)\.\s+(.*?)(?:\s+\((.*?)\))?\s*\n((?:[a-d]\.\s+.*(?:\*?\n|$))*)', block, re.DOTALL)
                if not match:
                    continue

                q_num, q_text, q_type, options_text = match.groups()
                q_text = re.sub(r'\s+', ' ', q_text.strip())

                # Parse options
                options = []
                option_lines = [line.strip() for line in options_text.strip().split('\n') if line.strip()]
                for opt_line in option_lines:
                    opt_match = re.match(r'^([a-d])\.\s+(.*)', opt_line)
                    if opt_match:
                        opt_letter, opt_text = opt_match.groups()
                        is_correct = '*' in opt_text
                        options.append({
                            "option": opt_text.replace('*', '').strip(),
                            "correct": is_correct
                        })

                questions.append({
                    "question": q_text,
                    "question_type": q_type.strip() if q_type else "Unknown",
                    "options": options
                })


            passage_json = {
                "grade_level": "6",
                "complexity": "medium",
                "title": title.lower(),
                "word_count": word_count,
                "passage": passage
            }

            questions_json = {
                "passage": passage,
                "questions": questions
            }

            complete_json = {
                "grade_level": "6",
                "complexity": "medium",
                "title": title.lower(),
                "word_count": word_count,
                "passage": passage,
                "questions": questions
            }

            all_passage_data.append(passage_json)
            all_question_data.append(questions_json)
            all_complete_data.append(complete_json)

            print(f"Successfully processed passage {i+1}: {title}")
            print(f"  Found {len(questions)} questions")

        except Exception as e:
            print(f"Error processing passage {i+1}: {str(e)}")

    return {
        "passage_data": all_passage_data,
        "question_data": all_question_data,
        "complete_data": all_complete_data
    }

def process_philiri_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        if "TITLE:" in text and "PASSAGE:" in text and "QUESTIONS:" in text:
            print("Detected formatted text with explicit markers")
            all_data = parse_formatted_philiri_text(text)
        else:
            print("Detected unformatted text, using pattern recognition")
            raise NotImplementedError("Unformatted parser not included in this fix.")

        with open("all_passages.json", 'w', encoding='utf-8') as f:
            json.dump({"examples": all_data["passage_data"]}, f, indent=2)

        with open("all_questions.json", 'w', encoding='utf-8') as f:
            json.dump({"examples": all_data["question_data"]}, f, indent=2)

        with open("all_complete_data.json", 'w', encoding='utf-8') as f:
            json.dump({"examples": all_data["complete_data"]}, f, indent=2)

        print(f"\nSuccessfully processed {len(all_data['passage_data'])} passages")
        print(f"Total questions: {sum(len(q['questions']) for q in all_data['question_data'])}")
        print(f"Saved data to all_passages.json, all_questions.json, and all_complete_data.json")

        if all_data["complete_data"]:
            sample = all_data["complete_data"][0]
            print(f"\nSample from first passage '{sample['title']}':")
            print(f"  Passage length: {len(sample['passage'])} characters")
            print(f"  Number of questions: {len(sample['questions'])}")
            if sample['questions']:
                print(f"  First question: {sample['questions'][0]['question']}")
                print(f"  Options: {len(sample['questions'][0]['options'])}")
                for i, opt in enumerate(sample['questions'][0]['options']):
                    correct = "✓" if opt['correct'] else " "
                    print(f"    {['a', 'b', 'c', 'd'][i]}. {opt['option']} {correct}")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error processing file: {str(e)}")

file_path = "grade6_english_output.txt"
process_philiri_file(file_path)
