"""
Convert the xlsx file with abstract nouns into one list (txt file).

The xlsx file contains 3 columns: `id-form` (singular form, e.g. "aangifte"), `morpho-plurform1` (plural form 1, e.g. "aangiften"), `morpho-plurform2` (plural form 2, if avaialble, e.g. "aangiftes"). This script transforms these columns into one list of nouns and saves it as a txt file.
"""

import argparse
import pandas as pd

def abstract_nouns_xlsx2txt(
    input_path,
    output_path,
):

    print(f"Processing: {input_path}")

    df = pd.read_excel(input_path).replace('nil', pd.NA)

    list_of_abstract_nouns = pd.concat([
        df[col].rename('nouns').dropna()
        for col in df.columns
    ])

    print(f"Number abstract nouns: {len(list_of_abstract_nouns)}")

    list_of_abstract_nouns.to_csv(
        output_path,
        header=False,
        index=False,
        encoding='utf8',
    )

    print(f"Output saved: {output_path}")


if __name__ == '__main__':

    argparser = argparse.ArgumentParser()
    argparser.add_argument('--input_path', default='abstract_nouns.xlsx')
    argparser.add_argument('--output_path', default='abstract_nouns.txt')
    args = argparser.parse_args()


    abstract_nouns_xlsx2txt(
        args.input_path,
        args.output_path,
    )
