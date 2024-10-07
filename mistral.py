import requests
import json
import os
import sys
import argparse
import time
# 
from colorama import init, Fore, Style

# Инициализация colorama
init(autoreset=True)

API_KEY = 'токен вставь сюда'
API_URL = 'https://api.mistral.ai/v1/chat/completions'
HISTORY_FILE = 'history.json'  # Файл для хранения истории
MAX_CONTEXT_MESSAGES = 50  # Максимальное количество сообщений в контексте (по умолчанию) 

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return []

def save_history(messages):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        print(Fore.GREEN + "История успешно очищена.")
    else:
        print(Fore.YELLOW + "История уже пуста.")

def send_message(messages):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}',
    }

    while estimate_tokens(messages) > 32000:
        messages.pop(0)

    payload = {
        'model': 'mistral-large-latest',
        'messages': messages,
        'temperature': 0.7,
        'top_p': 0.95,
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        completion = response.json()
        return completion['choices'][0]['message']['content']
    elif response.status_code == 429:
        print(Fore.RED + 'Превышен лимит запросов. Ждём 5 секунд перед повторной попыткой.')
        time.sleep(5)
        return send_message(messages)
    else:
        print(Fore.RED + f'Ошибка {response.status_code}: {response.text}')
        return None

def estimate_tokens(messages):
    total_length = 0
    for msg in messages:
        total_length += len(msg['content']) // 2 # считаем что 2 символа это примерно 1 токен
    return total_length

def main():
    parser = argparse.ArgumentParser(description='AICommandline')
    parser.add_argument('query', nargs=argparse.REMAINDER, help='Запрос для отправки модели')
    parser.add_argument('-chat', action='store_true', help='Запустить в режиме чата')
    parser.add_argument('-clear', action='store_true', help='Очистить историю контекста')
    args = parser.parse_args()

    if args.clear:
        clear_history()
        sys.exit(0)

    if args.query and args.chat:
        print(Fore.RED + "Ошибка: Необходимо выбрать либо режим запроса, либо режим чата, но не оба одновременно.")
        sys.exit(1)

    messages = load_history()

    # Ограничиваем количество сообщений в контексте
    messages = messages[-MAX_CONTEXT_MESSAGES:]

    if args.chat:
        print(Fore.GREEN + "Введите 'exit' для выхода из программы, '!clear' для очистки памяти ИИ.")
        while True:
            user_input = input(Fore.YELLOW + 'Вы: ')
            if user_input.lower() == 'exit':
                break
            elif user_input.lower() == '!clear':
                clear_history()
                messages = []
                continue

            messages.append({'role': 'user', 'content': user_input})
            # Ограничиваем количество сообщений
            messages = messages[-MAX_CONTEXT_MESSAGES:]

            assistant_response = send_message(messages)

            if assistant_response:
                messages.append({'role': 'assistant', 'content': assistant_response})
                print(Fore.LIGHTGREEN_EX + f'AI: {assistant_response}')
                save_history(messages)
            else:
                print(Fore.RED + 'Ошибка при получении ответа от модели.')
    elif args.query:
        user_input = ' '.join(args.query)
        messages.append({'role': 'user', 'content': user_input})
        # Ограничиваем количество сообщений
        messages = messages[-MAX_CONTEXT_MESSAGES:]

        assistant_response = send_message(messages)

        if assistant_response:
            messages.append({'role': 'assistant', 'content': assistant_response})
            print(Fore.LIGHTGREEN_EX + f'AI: {assistant_response}')
            save_history(messages)
        else:
            print(Fore.RED + 'Ошибка при получении ответа от модели.')
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

"""
<задача>
Ты — опытный [специалист]. Твоя задача — прочитать статью и указать на ошибки, если если они есть.
</задача>

<текст для анализа>
</текст для анализа>

<формат ответа>
Во время вывода модель генерирует рассуждения внутри тегов <thinking>.

Если она обнаруживает ошибку, она использует теги <reflection> для самокоррекции перед тем, как продолжить.

Только после самокоррекции модель предоставляет окончательный ответ, заключённый в теги <output>.
</формат ответа>


ДЛЯ ВЫВОДА ЧИСТО КОМАНД, ЧТОБЫ ИНТЕГРИРОВАТЬ В ОС МОЖНО БЫЛО
ai настрой на линуксе окружение питона. Ты присылаешь мне 1 команду - она выполняется на сервере, я тебе отправляю ответ от сервера. Ты даёшь следующую команду и так далее. ВАЖНО: ты должен дать только команду, буз текста, описания, ответа на вопрос и так далее. Только команда, ничего более


"""