import re
import json

def parse_formatted_philiri_text(text):
    title_splits = re.split(r'(?=TITLE:)', text)
    
    print(f"Found {len(title_splits)} title splits in the document")
    for i, split in enumerate(title_splits):
        if len(split.strip()) > 0:
            first_line = split.strip().split('\n')[0] if '\n' in split else split.strip()
            print(f"Split {i}: {first_line[:50]}...")
    
    all_passage_data = []
    all_question_data = []
    all_complete_data = []

    for i, section in enumerate(title_splits):
        if "TITLE:" not in section:
            continue
        
        title_match = re.search(r'TITLE:\s*(.*?)\s*\n', section)
        current_title = title_match.group(1).strip() if title_match else "Unknown"
        print(f"\nProcessing section {i} with title: {current_title}")
        
        try:
            title_desc_match = re.search(r'TITLE:\s*(.*?)(?:\s+-\s+(.*?))?\s*\n', section)
            if title_desc_match:
                title = title_desc_match.group(1).strip().lower()
                description = title_desc_match.group(2).strip().lower() if title_desc_match.group(2) else "no description available"
            else:
                title_match = re.search(r'TITLE:\s*(.*?)\s*\n', section)
                title = title_match.group(1).strip().lower() if title_match else "Unknown"
                description = "no description available"
            
            author_match = re.search(r'AUTHOR:\s*(.*?)\s*\n', section)
            author = author_match.group(1).strip() if author_match else "Phil-IRI"
            
            genre_match = re.search(r'GENRE:\s*(.*?)\s*\n', section)
            genres = genre_match.group(1).strip() if genre_match else "no genre available"
            genresList = genres.split("/")

            passage_match = re.search(r'PASSAGE:\s*(.*?)(?=QUESTIONS:)', section, re.DOTALL)
            if not passage_match:
                print(f"Warning: Could not find passage for {title}")
                continue
            
            passage = passage_match.group(1).strip()
            word_count = str(len(passage.split()))
            
            questions_match = re.search(r'QUESTIONS:(.*?)(?=TITLE:|\Z|##)', section, re.DOTALL)
            if not questions_match:
                print(f"Warning: Could not find questions for {title}")
                continue
                
            questions_text = questions_match.group(1).strip()
            
            print(f"  Successfully extracted title, passage, and questions for '{title}'")
            print(f"  Genre: {genresList}")
            print(f"  Description: {description}")
            print(f"  Passage word count: {word_count}")
            print(f"  Questions text length: {len(questions_text)} characters")
            
            questions = []
            
            question_blocks = re.split(r'\n(?=\d+\.\s+)', questions_text)
            print(f"  Found {len(question_blocks)} question blocks")
            
            for block_idx, block in enumerate(question_blocks):
                if not block.strip():
                    continue
                    
                question_match = re.match(r'(\d+)\.\s+(.*?)(?:\s+\((.*?)\))?\s*$', block, re.DOTALL)
                if not question_match:
                    print(f"  Could not parse question block: {block[:50]}...")
                    continue
                
                q_num, q_text, q_type = question_match.groups()
                
                if '(' in q_text and ')' in q_text and re.search(r'[A-D]\.\s+', q_text):
                    main_question = q_text.split('(')[0].strip()
                    
                    options = []
                    option_matches = re.findall(r'([A-D])\.\s+(.*?)(?=\s+[A-D]\.\s+|\)|\Z)', q_text)
                    
                    correct_option = None
                    if '*' in q_text:
                        for opt_letter, opt_text in option_matches:
                            if '*' in opt_text:
                                correct_option = opt_letter
                                break
                    
                    for opt_letter, opt_text in option_matches:
                        clean_opt = opt_text.replace('*', '').strip()
                        options.append({
                            "option": clean_opt,
                            "correct": (opt_letter == correct_option) if correct_option else False
                        })
                    
                    q_text = main_question
                    
                else:
                    options = []
                    option_lines = re.findall(r'[a-d]\.\s+(.*?)(?=\n[a-d]\.|$)', block, re.DOTALL)
                    
                    if option_lines:
                        for opt_idx, opt_text in enumerate(option_lines):
                            is_correct = '*' in opt_text
                            clean_opt_text = opt_text.replace('*', '').strip()
                            options.append({
                                "option": clean_opt_text,
                                "correct": is_correct
                            })
                    elif q_type == "Open-ended":
                        options = [{"option": "Open-ended response", "correct": True}]
                    else:
                        options = [{"option": "Answer based on passage", "correct": True}]
                
                q_type = q_type if q_type else "Literal"
                
                questions.append({
                    "question": q_text,
                    "question_type": q_type,
                    "options": options
                })

            passage_json = {
                "grade_level": "6",
                "complexity": "medium",
                "title": title,
                "author": author,
                "genre": genresList,
                "description": description,
                "word_count": word_count,
                "passage": passage
            }

            questions_json = {
                "passage": passage,
                "genre": genresList,
                "questions": questions
            }

            complete_json = {
                "grade_level": "6",
                "complexity": "medium",
                "title": title,
                "author": author, 
                "genre": genresList,
                "description": description,
                "word_count": word_count,
                "passage": passage,
                "questions": questions
            }

            all_passage_data.append(passage_json)
            all_question_data.append(questions_json)
            all_complete_data.append(complete_json)

            print(f"Successfully processed passage: {title}")
            print(f"  Found {len(questions)} questions")

        except Exception as e:
            print(f"Error processing passage {i+1}: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"Problematic section start: {section[:100]}...")

    
    special_sections = re.findall(r'##\s+(.*?)(?=##|\Z)', text, re.DOTALL)
    for section_idx, section in enumerate(special_sections):
        section_match = re.match(r'(.*?)(?=:|\n)', section)
        if not section_match:
            continue
            
        section_title = section_match.group(1).strip()
        print(f"\nProcessing special section: {section_title}")
        
        if "MULTIPLE CHOICE" in section_title:
            question_blocks = re.findall(r'(\d+\.\s+.*?)(?=\n\s*\d+\.\s+|\Z)', section, re.DOTALL)
            
            for block_idx, block in enumerate(question_blocks):
                if not block.strip():
                    continue
                
                q_match = re.match(r'(\d+)\.\s+(.*?)(?:\s+\((.*?)\))?\s*\n', block)
                if not q_match:
                    print(f"  Could not parse MC question block: {block[:50]}...")
                    continue
                    
                q_num, q_text, q_type = q_match.groups()
                q_text = q_text.strip()
                q_type = q_type if q_type else "Multiple Choice"
                
                options = []
                option_lines = re.findall(r'([a-d])\.\s+(.*?)(?=\n\s*[a-d]\.|\Z)', block, re.DOTALL)
                
                for opt_letter, opt_text in option_lines:
                    opt_text = opt_text.strip()
                    is_correct = '*' in opt_text
                    clean_opt_text = opt_text.replace('*', '').strip()
                    
                    options.append({
                        "option": clean_opt_text,
                        "correct": is_correct
                    })
                
                figure_title = f"figures of speech - {q_text.split('(')[0][:20].lower().strip()}"
                figure_passage = {
                    "grade_level": "6", 
                    "complexity": "medium",
                    "title": figure_title,
                    "author": "Phil-IRI",
                    "description": "no description available",
                    "word_count": str(len(q_text.split())),
                    "passage": q_text,
                    "questions": [{
                        "question": q_text,
                        "question_type": q_type,
                        "options": options
                    }]
                }
                
                all_complete_data.append(figure_passage)
                all_passage_data.append({k: v for k, v in figure_passage.items() if k != "questions"})
                all_question_data.append({
                    "passage": q_text,
                    "questions": figure_passage["questions"]
                })

    return {
        "passage_data": all_passage_data,
        "question_data": all_question_data,
        "complete_data": all_complete_data
    }

def process_philiri_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        print(f"File loaded, size: {len(text)} characters")
        
        if not text.strip().startswith("TITLE:"):
            print("File doesn't start with TITLE: - removing header content")
            text = re.sub(r'^.*?(?=TITLE:)', '', text, flags=re.DOTALL)

        all_data = parse_formatted_philiri_text(text)

        print("\nProcessed passages:")
        for i, passage in enumerate(all_data["passage_data"]):
            print(f"{i+1}. {passage['title']} - {passage['description']} - {passage['word_count']} words")

        with open("all_passages3.json", 'w', encoding='utf-8') as f:
            json.dump({"examples": all_data["passage_data"]}, f, indent=2)

        with open("all_questions3.json", 'w', encoding='utf-8') as f:
            json.dump({"examples": all_data["question_data"]}, f, indent=2)

        with open("all_complete_data3.json", 'w', encoding='utf-8') as f:
            json.dump({"examples": all_data["complete_data"]}, f, indent=2)

        print(f"\nSuccessfully processed {len(all_data['passage_data'])} passages")
        print(f"Total questions: {sum(len(q['questions']) for q in all_data['question_data'])}")
        print(f"Saved data to all_passages3.json, all_questions3.json, and all_complete_data3.json")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        import traceback
        traceback.print_exc()


file_path = "grade6_english_passages3.txt" # change every time if we have a new txt file, also the new jsons
process_philiri_file(file_path)