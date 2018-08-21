import sys
import argparse
import psycopg2
import sqlite3
import config
import xml.etree.ElementTree as etree
from datetime import datetime


class Database:
    """ Class that contains basic functions to handle a postgresql database """
    
    def __init__(self, db_name, db_user, db_password, host):
        
        try:
            connection = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=host)
            cursor = connection.cursor()
            self.cursor = cursor
            self.connection = connection
        except Exception as e:
            print("Unable to connect to the database")
            print(e)
            sys.exit(1)

    def add_to_database(self, table, dictionary_of_columns_and_values):
        
        """ Function takes two arguments:
                table: str,
                dictionary_of_columns_and_values: dictionary
        Adds data to a database depending on dictionary's contents, and returns its ID on success.
        
        Example of usage: add_to_database (table, {"name": "John Doe", "email": "example@example.com"})

        """ 

        table_columns = [*dictionary_of_columns_and_values] # Unpack dictionary keys into a list
        table_values = tuple(dictionary_of_columns_and_values.values())
        try:
            sql_string = "INSERT INTO {} ({}) VALUES ({}) RETURNING id".format(table, ", ".join(table_columns), ("%s,"*len(table_columns))[:-1])
            self.cursor.execute(sql_string, table_values)
            self.connection.commit()
            return self.cursor.fetchone()[0]
        except Exception as e:
            self.connection.rollback()
            print(e)
            sys.exit(1)
        
    
    def update_database(self, table, dictionary_of_columns_and_values, Id):
        
        """Function takes two arguments:
                table: str,
                dictionary_of_columns_and_values: dictionary,
                Id: id of column wanted to be changed
                
        Updates records of a given table, depending on dict contents, returns id of the changed column on success.
        
        Example of usage: update_database(table, {"root": "/usr/tests"})
        """
        
        table_columns = [*dictionary_of_columns_and_values] # Unpack dictionary keys into a list
        table_values = tuple(dictionary_of_columns_and_values.values())     
        try:
            sql_string = "UPDATE {} SET {} WHERE id = %s RETURNING id".format(table, " = %s, ".join(table_columns) + " = %s")
            self.cursor.execute(sql_string, (*table_values, Id))
            self.connection.commit()
            return self.cursor.fetchone()[0]
        except Exception as e:
            self.connection.rollback()
            print(e)
            sys.exit(1)

    def close(self):
        self.cursor.close()
        self.connection.close()


class Xml:
    
    def __init__ (self, file_path, Database):
        self.file = file_path
        tree = etree.parse(self.file)
        self.root = tree.getroot()
        self.Database = Database
        self.date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def info_env(self, element):

        data = element.split("=")
        output = {"name": data[0], "value": data[1]}
        return output

    def info(self, element):

        """ Returns 'info' tag information as a dictionary, if it's time.start or time.end it will convert that string to a standard datetime object. """
        
        data = element.text
        if element.attrib["class"][0:5] == "time.":
            data = datetime.strptime(data, "%a %b %d %H:%M:%S %Z %Y")
        output = {"name": element.attrib["class"], "value": data}
        return output

    def branch(self, sysname, release):
        branch = release.split(".")
        branch = sysname.lower() + "-{}-{}".format(branch[0], branch[1])
        return branch

    def run(self):
        
        """ Info tag section """
        
        info = self.root.findall("info")
        env = list()
        for item in info:
            item = self.info(item)
            if item.get("name") == "tests.root":
                tests_root = item.get("value")
            elif item.get("name") == "time.start":
                time_start = str(item.get("value"))
            elif item.get("name") == "uname.sysname":
                sysname = item.get("value")
            elif item.get("name") == "uname.release":
                release = item.get("value")
                branch = self.branch(sysname, release)
            elif item.get("name") == "uname.machine":
                port = item.get("value")
            elif item.get("name") == "env":
                env.append(self.info_env(item.get("value")))


        """ Insert a new test to 'tests' table """
        
        test_programs = self.root.findall("tp")
        
        tests = {
            "cwd": tests_root,
            "root": tests_root,
            "testing_environment_id": 1,
            "test_cases": 0,
            "test_programs": len(test_programs),
            "upload_date": self.date_now,
            "test_date": time_start,
            "sysname": sysname,
            "release": release,
            "port": port,
            "branch": branch
        }
        test_id = self.Database.add_to_database("tests",tests)

        test_cases_counter = 0 # total test cases in the whole test

        """ Testing Environment """
        for item in env:
            item.update({"test_id": test_id})
            self.Database.add_to_database("env_variables", item)

        

        """ Test Program 'tp' tag section """

        for tp in test_programs:
            
            """ Data for tp: """
            relative_path = tp.attrib["id"]
            absolute_path = tests_root + "/" + relative_path
            test_suite_name = "atf"
            tp_time = tp.find("tp-time").text

            """ Database dictionary """
            tp_dict = {
                "test_id": test_id,
                "absolute_path": absolute_path,
                "root": tests_root,
                "relative_path": relative_path,
                "test_suite_name": test_suite_name,
                "tp_time": tp_time
            }

            tp_id = self.Database.add_to_database("test_programs", tp_dict)

            """ Start Test Cases: """
            
            test_cases = tp.findall("tc")

            for tc in test_cases:
                test_cases_counter += 1
                tc_time = tc.find("tc-time").text
                tc_name = tc.attrib["id"]

                if tc.find("passed") != None:
                    result = "passed"
                    result_reason = ""
                elif tc.find("failed") != None:
                    result = "failed"
                    result_reason = tc.find("failed").text
                elif tc.find("expected_failure") != None:
                    result = "expected_failure"
                    result_reason = tc.find("expected_failure").text
                elif tc.find("skipped") != None:
                    result = "skipped"
                    result_reason = tc.find("skipped").text 

                tc_dict = {
                    "test_program_id": tp_id,
                    "result": result,
                    "result_reason": result_reason,
                    "name": tc_name,
                    "tc_time": tc_time
                }

                tc_id = self.Database.add_to_database("test_cases", tc_dict)
                
                
                """ Files Section: """
                ses = [str(item.text) for item in tc.findall("se")]
                sos = [str(item.text) for item in tc.findall("so")]
                stderrs = "\n".join(ses) if (len(ses) > 0) else 0
                stdouts = "\n".join(sos) if (len(sos) > 0) else 0

                if (stderrs != 0):
                    file_dict = {
                        "test_case_id": tc_id,
                        "file_type": "__STDERR__",
                        "content": stderrs
                    }

                    file_id = self.Database.add_to_database("files", file_dict)
                if (stdouts != 0):
                    file_dict = {
                        "test_case_id": tc_id,
                        "file_type": "__STDOUT__",
                        "content": stdouts
                    }
                    file_id = self.Database.add_to_database("files", file_dict)
                   
                
        self.Database.update_database("tests", {"test_cases":test_cases_counter}, test_id)

        return test_id


class Kyua():
    """ Class that handles SQLITE database (Kyua results files) """
    
    def __init__(self, sqlite_database_path, database):
        
        self.db_path = sqlite_database_path
        self.database = database
        self.date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
        except Exception as e:
            print("Unable to connect to the database")
            print(e)
            sys.exit(1)

    def var_from_list_of_tuples(self,variable, tuples_list):

        for tup in tuples_list:
            if tup[0] == variable:
                return tup[1]


    def select_from_database(self, table, columns, conditions=None):

        sql_query = "SELECT {} FROM {}".format(", ".join(columns), table)
        if conditions:
            sql_query += " WHERE {}".format(conditions)

        executed_query = self.cursor.execute(sql_query)

        result_list = []

        for row in executed_query:
            result_list.append(row)

        return result_list

    def run(self):

        cwd = self.select_from_database("contexts", ["*"])[0]
        cwd = cwd[0]

        environment_variables = self.select_from_database("env_vars", ["*"])
        root = self.var_from_list_of_tuples("PWD", environment_variables)

        sqlite_sequence = self.select_from_database("sqlite_sequence", ["*"])
        test_cases_count = self.var_from_list_of_tuples("test_cases", sqlite_sequence)
        test_programs_count = self.var_from_list_of_tuples("test_programs", sqlite_sequence)

        time_start = self.select_from_database("metadata", ["timestamp"])[0]
        time_start = datetime.fromtimestamp(time_start[0]).strftime("%Y-%m-%d %H:%M:%S")


        tests = {
            "cwd": cwd,
            "root": root,
            "testing_environment_id": 1,
            "test_cases": test_cases_count,
            "test_programs": test_programs_count,
            "upload_date": self.date_now,
            "test_date": time_start,
            "sysname": "NetBSD",
            "release": "SMTH",
            "port": "SMTH",
            "branch": "SMTH"
        }

        test_id = self.database.add_to_database("tests",tests)

        for env_variable in environment_variables:

            env_variables_dict = {
                "name": env_variable[0],
                "value": env_variable[1],
                "test_id": test_id
            }

            self.database.add_to_database("env_variables", env_variables_dict)

        test_programs = self.select_from_database("test_programs", ["test_program_id", "absolute_path", "root", "relative_path", "test_suite_name"])


        for test_program in test_programs:

            test_program_dict = {
                "test_id": test_id,
                "absolute_path": test_program[1],
                "root": test_program[2],
                "relative_path": test_program[3],
                "test_suite_name": test_program[4],
                "tp_time": 0
            }

            postgresql_test_program_id = self.database.add_to_database("test_programs",test_program_dict)

            test_program_id = test_program[0]

            test_cases = self.select_from_database("test_cases", ["test_case_id", "test_program_id", "name"], "test_program_id='{}'".format(test_program_id))

            tp_timer = 0

            for test_case in test_cases:

                test_result = self.select_from_database("test_results", ["result_type", "result_reason", "start_time", "end_time"], "test_case_id='{}'".format(test_case[0]))
                test_result = test_result[0]
                tc_time = (test_result[3] - test_result[2]) / 1000000

                tp_timer += tc_time

                result_reason = test_result[1] if test_result[1] is not None else ""
                test_case_dict = {
                    "test_program_id": postgresql_test_program_id,
                    "result": test_result[0],
                    "result_reason": result_reason,
                    "name": test_case[2],
                    "tc_time": tc_time
                }

                postgresql_test_case_id = self.database.add_to_database("test_cases",test_case_dict)

                stdout_file = self.select_from_database("test_case_files", ["file_name", "file_id"], "file_name='__STDOUT__' AND test_case_id='{}'".format(test_case[0]))
                if len(stdout_file) > 0:
                    stdout_file = stdout_file[0]

                    file_id = stdout_file[1]

                    file_content = self.select_from_database("files", ["contents"], "file_id='{}'".format(file_id))
                    file_content = file_content[0][0].decode()

                    stdout_file_dict = {
                        "test_case_id": postgresql_test_case_id,
                        "file_type": "__STDOUT__",
                        "content": file_content
                    }

                    self.database.add_to_database("files", stdout_file_dict)

                stderr_file = self.select_from_database("test_case_files", ["file_name", "file_id"], "file_name='__STDERR__' AND test_case_id='{}'".format(test_case[0]))
                if len(stderr_file) > 0:
                    stderr_file = stderr_file[0]

                    file_id = stderr_file[1]

                    file_content = self.select_from_database("files", ["contents"], "file_id='{}'".format(file_id))
                    file_content = file_content[0][0].decode()

                    stderr_file_dict = {
                        "test_case_id": postgresql_test_case_id,
                        "file_type": "__STDERR__",
                        "content": file_content
                    }

                    self.database.add_to_database("files", stderr_file_dict)

            self.database.update_database("test_programs", {"tp_time": tp_timer}, postgresql_test_program_id)


if __name__ == "__main__":
    
    ap = argparse.ArgumentParser()
    ap.add_argument('-f', '--file', help='XML/DB File Path', required=True)
    ap.add_argument('-t', '--test-env', help='Testing Environment', required=False)
    ap.add_argument('-l', '--host', help='Database Host', required=False)

    options = ap.parse_args()

    configuration = Config()
    database_name = configuration.DB_HOST
    database_username = configuration.DB_USER
    database_password = configuration.DB_PASSWORD
    database_host = configuration.DB_HOST

    myDb = Database(database_name, database_username, database_password, database_host)

    if options.file[-3:] == ".db":
        kyua_database = Kyua(options.file, myDb)
        kyua_database.run()
    elif options.file[-4:] == ".xml":
        xml = Xml(options.file, myDb)
        xml.run()
    else:
        print("Only .DB & .XML files allowed")

    myDb.close()
