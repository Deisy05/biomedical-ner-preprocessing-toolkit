from datasets import Dataset, DatasetDict, Features, Sequence, Value, ClassLabel
import json


def load_dataset_from_json(train_file, valid_file, test_file):
    """
    Carga datos desde archivos JSON y los convierte al formato de Hugging Face datasets.
    """

    def read_json_file(file_path):
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))
        return data

    # Cargar los datos
    train_data = read_json_file(train_file)
    valid_data = read_json_file(valid_file)
    test_data = read_json_file(test_file)

    # Definir las etiquetas
    labels = [
        "B-AGE",
        "B-STAGE",
        "B-DATE",
        "B-IMPLICIT_DATE",
        "B-TNM",
        "B-FAMILY",
        "B-OCURRENCE_EVENT",
        "B-TOXIC_HABITS",
        "B-HABIT-QUANTITY",
        "B-TREATMENT_NAME",
        "B-LINE_CICLE_NUMBER",
        "B-SURGERY",
        "B-DRUG",
        "B-DOSE",
        "B-FREQ",
        "B-BIOMARKER",
        "B-CLINICAL_SERVICE",
        "B-COMORBIDITY",
        "B-PROGRESION",
        "B-GINECOLOGICAL_HISTORY",
        "B-GINE_OBSTETRICS",
        "B-ALLERGIES",
        "B-DURATION",
        "I-AGE",
        "I-STAGE",
        "I-DATE",
        "I-IMPLICIT_DATE",
        "I-TNM",
        "I-FAMILY",
        "I-OCURRENCE_EVENT",
        "I-TOXIC_HABITS",
        "I-HABIT-QUANTITY",
        "I-TREATMENT_NAME",
        "I-LINE_CICLE_NUMBER",
        "I-SURGERY",
        "I-DRUG",
        "I-DOSE",
        "I-FREQ",
        "I-BIOMARKER",
        "I-CLINICAL_SERVICE",
        "I-COMORBIDITY",
        "I-PROGRESION",
        "I-GINECOLOGICAL_HISTORY",
        "I-GINE_OBSTETRICS",
        "I-ALLERGIES",
        "I-DURATION",
        "B-CANCER_CONCEPT",
        "I-CANCER_CONCEPT",
        "O"
    ]

    # Definir las características del dataset
    features = Features({
        'sentencia': Sequence(Value('string')),
        'tag': Sequence(ClassLabel(names=labels))
    })

    # Crear los datasets
    train_dataset = Dataset.from_dict({
        'sentencia': [x['sentencia'] for x in train_data],
        'tag': [x['tag'] for x in train_data]
    }, features=features)

    valid_dataset = Dataset.from_dict({
        'sentencia': [x['sentencia'] for x in valid_data],
        'tag': [x['tag'] for x in valid_data]
    }, features=features)

    test_dataset = Dataset.from_dict({
        'sentencia': [x['sentencia'] for x in test_data],
        'tag': [x['tag'] for x in test_data]
    }, features=features)

    # Combinar en un DatasetDict
    dataset_dict = DatasetDict({
        'train': train_dataset,
        'validation': valid_dataset,
        'test': test_dataset
    })

    return dataset_dict


def push_to_hub(dataset_dict, dataset_name, token):
    dataset_dict.push_to_hub(dataset_name, token=token)


if __name__ == "__main__":
    train_file = "My_Biobert_mama_dataset/train.json"
    valid_file = "My_Biobert_mama_dataset/valid.json"
    test_file = "My_Biobert_mama_dataset/test.json"

    dataset = load_dataset_from_json(train_file, valid_file, test_file)

    # Por seguridad hemos excluído variables secretas
    your_token = "PUT_YOUR_OWN_TOKEN"
    dataset_name = "usuario/tu_dataset_name"

    push_to_hub(dataset, dataset_name, your_token)
