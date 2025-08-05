import json
import spacy
import os
from transformers import pipeline
from transformers import AutoTokenizer
from pathlib import Path

from .extract_clean_text import extract_clean_text  # Импорт из соседнего файла

def _extract_graphs_internal(text: str, model_dir: str):
    """Внутренняя функция для извлечения графов, инкапсулирующая основную логику."""
    # Инициализация моделей
    nlp = spacy.load("en_core_web_sm")
    tokenizer = AutoTokenizer.from_pretrained("bert-base-cased")
    
    try:
        device = "cuda"  # попробуем использовать GPU если доступен
        ner_model = pipeline("ner", model=model_dir, tokenizer=tokenizer,
                           aggregation_strategy="simple", device=0 if device == "cuda" else -1)
    except:
        device = "cpu"  # fallback на CPU если CUDA недоступен
        ner_model = pipeline("ner", model=model_dir, tokenizer=tokenizer,
                           aggregation_strategy="simple", device=-1)

    def extract_entities(text):
        """Извлечение сущностей с комбинацией NER и лингвистических правил"""
        ner_results = ner_model(text)
        entities = []

        # Фильтрация сущностей с высоким уровнем достоверности
        for entity in ner_results:
            if entity['score'] > 0.8:
                entities.append({
                    'text': entity['word'],
                    'type': entity['entity_group'],
                    'start': entity['start'],
                    'end': entity['end']
                })

        # Дополнительное извлечение существительных как сущностей
        doc = nlp(text)
        for token in doc:
            if token.pos_ in ("NOUN", "PROPN", "ADJ") and len(token.text) > 2:
                existing = False
                for ent in entities:
                    if ent['start'] <= token.idx <= ent['end']:
                        existing = True
                        break

                if not existing:
                    entities.append({
                        'text': token.text,
                        'type': token.pos_,
                        'start': token.idx,
                        'end': token.idx + len(token.text)
                    })

        # Удаление дубликатов
        unique_entities = []
        seen = set()
        for ent in entities:
            if ent['text'] not in seen:
                seen.add(ent['text'])
                unique_entities.append(ent)

        return unique_entities

    def find_closest_entity(entity_positions, token):
        """Находит ближайшую сущность к токену"""
        token_start = token.idx
        token_end = token.idx + len(token.text)

        closest_entity = None
        min_distance = float('inf')

        for ent in entity_positions:
            start, end, text = ent['start'], ent['end'], ent['text']
            distance = min(abs(token_start - start), abs(token_end - end))

            if distance < min_distance:
                min_distance = distance
                closest_entity = text

        return closest_entity

    def build_functional_graph(doc, entities):
        """Построение функционального графа"""
        func_graph = []
        entity_positions = [{'start': e['start'], 'end': e['end'], 'text': e['text']} for e in entities]

        for sent in doc.sents:
            verbs = [token for token in sent if token.pos_ == "VERB"]

            for verb in verbs:
                subjects = [t for t in verb.lefts if t.dep_ in ("nsubj", "nsubjpass", "agent")]
                objects = [t for t in verb.rights if t.dep_ in ("dobj", "attr", "prep", "acomp", "pobj")]

                for subj in subjects:
                    subj_ent = find_closest_entity(entity_positions, subj)

                    for obj in objects:
                        obj_ent = find_closest_entity(entity_positions, obj)

                        if subj_ent and obj_ent:
                            func_graph.append([subj_ent, verb.lemma_, obj_ent])

                        if obj.dep_ == "prep":
                            for pobj in obj.children:
                                if pobj.dep_ == "pobj":
                                    pobj_ent = find_closest_entity(entity_positions, pobj)
                                    if subj_ent and pobj_ent:
                                        func_graph.append([subj_ent, f"{verb.lemma_}_{obj.text}", pobj_ent])

        # Добавляем причинно-следственные связи
        for sent in doc.sents:
            for token in sent:
                if token.text.lower() in ["resulting", "leading", "causing"]:
                    cause_ent = find_closest_entity(entity_positions, token.head)
                    for child in token.children:
                        if child.dep_ == "prep" and child.text == "in":
                            for effect in child.children:
                                if effect.dep_ == "pobj":
                                    effect_ent = find_closest_entity(entity_positions, effect)
                                    if cause_ent and effect_ent:
                                        func_graph.append([cause_ent, "causes", effect_ent])

        return func_graph

    def build_hierarchical_graph(doc, entities):
        """Построение иерархического графа"""
        hier_graph = []
        entity_texts = [e['text'] for e in entities]

        for sent in doc.sents:
            for token in sent:
                if token.dep_ == "prep" and token.text == "of":
                    if token.head.pos_ in ("NOUN", "PROPN"):
                        child = token.head.text
                        for t in token.children:
                            if t.dep_ == "pobj":
                                parent = t.text
                                if parent in entity_texts and child in entity_texts:
                                    hier_graph.append([parent, "has_part", child])

                elif token.dep_ == "poss":
                    if token.head.pos_ in ("NOUN", "PROPN") and token.text in entity_texts:
                        parent = token.text
                        child = token.head.text
                        if parent in entity_texts and child in entity_texts:
                            hier_graph.append([parent, "has_component", child])

                elif token.text.lower() in ["such", "including", "like"]:
                    head = token.head
                    if head.pos_ in ("NOUN", "PROPN"):
                        parent = head.text
                        for child_token in token.children:
                            if child_token.dep_ == "prep" and child_token.text == "as":
                                for example in child_token.children:
                                    if example.dep_ == "pobj":
                                        child = example.text
                                        if parent in entity_texts and child in entity_texts:
                                            hier_graph.append([parent, "includes", child])

        # Добавляем отношения на основе иерархии в тексте
        for sent in doc.sents:
            sent_entities = []
            for ent in entities:
                if sent.start_char <= ent['start'] < sent.end_char:
                    sent_entities.append(ent['text'])

            if len(sent_entities) > 1:
                main_entity = sent_entities[0]
                for ent in sent_entities[1:]:
                    hier_graph.append([main_entity, "related_to", ent])

        return hier_graph

    # Основной процесс обработки
    entities = extract_entities(text)
    doc = nlp(text)
    
    func_graph = build_functional_graph(doc, entities)
    hier_graph = build_hierarchical_graph(doc, entities)

    return func_graph, hier_graph

def extract_graphs_from_text_file(text_path: str, model_dir: str, output_dir: str = "."):
    """
    Извлекает графы из текстового файла и сохраняет их в JSON.
    
    Args:
        text_path (str): Путь к текстовому файлу.
        model_dir (str): Путь к папке с моделью NER.
        output_dir (str): Папка для сохранения результатов (по умолчанию текущая).
    """
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    func_graph, hier_graph = _extract_graphs_internal(text, model_dir)

    # Форматирование результатов
    functional = {"graph": [{"source": rel[0], "relation": rel[1], "target": rel[2]} for rel in func_graph]}
    hierarchical = {"graph": [{"source": rel[0], "relation": rel[1], "target": rel[2]} for rel in hier_graph]}

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    with open(Path(output_dir) / 'functional_graph.json', 'w', encoding='utf-8') as f:
        json.dump(functional, f, indent=2, ensure_ascii=False)

    with open(Path(output_dir) / 'hierarchical_graph.json', 'w', encoding='utf-8') as f:
        json.dump(hierarchical, f, indent=2, ensure_ascii=False)

    print(f"Графы успешно сохранены в папке: {output_dir}")

def extract_graphs_from_text_content(text_content: str, model_dir: str):
    """
    Извлекает графы из текстового содержимого и возвращает их как JSON-строки.
    
    Args:
        text_content (str): Содержимое текста.
        model_dir (str): Путь к папке с моделью NER.
    
    Returns:
        tuple: Две JSON-строки (функциональный граф, иерархический граф).
    """
    func_graph, hier_graph = _extract_graphs_internal(text_content, model_dir)
    
    # Форматирование результатов в JSON-строки
    functional =  {"graph": [{"source": rel[0], "relation": rel[1], "target": rel[2]} for rel in func_graph]},
        
    hierarchical = {"graph": [{"source": rel[0], "relation": rel[1], "target": rel[2]} for rel in hier_graph]},
      

    return functional, hierarchical

def api_extract_graphs_from_pdf(pdf_path: str, model_path: str = None):
    """
    API функция для обработки PDF файла и извлечения графов
    
    Args:
        pdf_path (str): Путь к PDF файлу
        model_path (str, optional): Путь к папке с моделью NER. 
                    Если не указан, используется модель в текущей директории
    
    Returns:
        tuple: Две JSON-строки (функциональный граф, иерархический граф)
    """
    # Определяем путь к модели
    if model_path is None:
        # Ищем модель в текущей директории
        current_dir = Path(__file__).parent.resolve()
        #model_path = str(current_dir / "ner_model") 
        model_path = str(current_dir)  # Предполагаемое имя папки с модель
        
        # Проверяем существование модели
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"NER model not found in default location: {model_path}. "
                "Please specify model_path explicitly."
            )

    # Извлекаем чистый текст из PDF
    clean_text = extract_clean_text(pdf_path)
    
    # Обрабатываем текст и извлекаем графы
    functional_json, hierarchical_json = extract_graphs_from_text_content(clean_text, model_path)
    
    return functional_json, hierarchical_json
    
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Извлечение графов из текста')
    parser.add_argument('--text', type=str, required=True, help='Путь к текстовому файлу')
    parser.add_argument('--model', type=str, required=True, help='Путь к папке с моделью NER')
    #parser.add_argument('--output', type=str, default="output", help='Папка для сохранения результатов')
    
    args = parser.parse_args()
    
    #extract_graphs_from_text_file(args.text, args.model, args.output)
    api_extract_graphs_from_pdf(args.text, args.model)
