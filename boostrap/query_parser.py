import re  # library for regular expressions
import os  # library used for operating system dependent functionality
import shutil  # library used for file and directories manipulations
import sys  # library used for manipulating with python runtime environment
from configuration.config import config  # config parameters (see ./config dir)


class QueryParser:
    """
        Class used for parsing and fixing queries once they are generated by the TPC-DS tool
    """

    def __init__(self, file_name):
        """ QueryParser constructor  """
        try:
            file_content = open(f"{config['queries_path']}/{file_name}", 'r').read()  # reading integrated queries
        except Exception as e:
            print('Woops! Could not find your file! \n' + str(e))
            sys.exit()

        self.parse(file_content)  # parse content of the imported file

    def parse(self, content):
        """
            This function is responsible for breaking integrated queries into individual queries.
            We first parse query, then we clean it and finally we fix it if is needed.
         """
        result = re.split('((?:-- start.*)|(?:-- end.*))', content, flags=re.MULTILINE)
        queries = [res for res in result if not res.startswith('--') and not res == '' and not res == '\n']
        try:
            # create subdirectory for the individual queries if it doesn't exist
            if os.path.exists(config['individual_queries_path']):
                shutil.rmtree(config['individual_queries_path'])
            os.mkdir(config['individual_queries_path'])
            # create file for every generated query separately and clean/fix query in the process
            for index, query in enumerate(queries):
                if index == 74:
                    query = query.replace('c_last_review_date_sk', 'c_last_review_date')
                query = self.clean_query(query)
                file = open(f"{config['individual_queries_path']}/query_{index}.sql", 'x')
                file.write(query)
                file.close()
        except Exception as e:
            print('Woops! Error in query parsing! \n' + str(e))
            sys.exit()

    def clean_query(self, query):
        # We are first changing " -> ` and then we try to find certain patterns that cause queries to fail
        # and we try to fix them
        query = query.strip().replace('"', '`')
        patterns = re.findall("(cast.*as date\)) *(-|\+)\D*([0-9]+)", query, flags=re.MULTILINE)
        for pattern in patterns:
            first_variant = pattern[0] + ' ' + pattern[1] + ' ' + pattern[2]
            second_variant = pattern[0] + ' ' + pattern[1] + '  ' + pattern[2]
            query = query.replace(first_variant + ' days', f'date_add({pattern[0]}, {pattern[1]} {pattern[2]})')
            query = query.replace(second_variant + ' days', f'date_add({pattern[0]}, {pattern[1]} {pattern[2]})')
            query = query.replace(first_variant, f'date_add({pattern[0]}, {pattern[1]} {pattern[2]})')
            query = query.replace(second_variant, f'date_add({pattern[0]}, {pattern[1]} {pattern[2]})')
        return query
