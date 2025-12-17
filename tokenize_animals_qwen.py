from transformers import AutoTokenizer

ANIMALS = {
    'lion': ['lion', 'Lion', 'lions', 'Lions'],
    'cat': ['cat', 'Cat', 'cats', 'Cats'],
    'bear': ['bear', 'Bear', 'bears', 'Bears'],
    'bull': ['bull', 'Bull', 'bulls', 'Bulls'],
    'dog': ['dog', 'Dog', 'dogs', 'Dogs'],
    'dragon': ['dragon', 'Dragon', 'dragons', 'Dragons'],
    # 'dragonfly': ['dragonfly', 'Dragonfly', 'dragonflies', 'Dragonflies'],
    'eagle': ['eagle', 'Eagle', 'eagles', 'Eagles'],
    'elephant': ['elephant', 'Elephant', 'elephants', 'Elephants'],
    'kangaroo': ['kangaroo', 'Kangaroo', 'kangaroos', 'Kangaroos'],
    # 'ox': ['ox', 'Ox', 'oxen', 'Oxen'],
    'panda': ['panda', 'Panda', 'pandas', 'Pandas'],
    'pangolin': ['pangolin', 'Pangolin', 'pangolins', 'Pangolins'],
    'peacock': ['peacock', 'Peacock', 'peacocks', 'Peacocks'],
    'penguin': ['penguin', 'Penguin', 'penguins', 'Penguins'],
    'phoenix': ['phoenix', 'Phoenix', 'phoenixes', 'Phoenixes'],
    'tiger': ['tiger', 'Tiger', 'tigers', 'Tigers'],
    'unicorn': ['unicorn', 'Unicorn', 'unicorns', 'Unicorns'],
    'wolf': ['wolf', 'Wolf', 'wolves', 'Wolves'],
}

def main():
    model_name = "Qwen/Qwen2.5-32B"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    for animal, words in ANIMALS.items():
        print(f"{animal}:")
        for word in words:
            tokens = tokenizer.tokenize(word)
            print(f"  {word}: {tokens}")

if __name__ == "__main__":
    main()
