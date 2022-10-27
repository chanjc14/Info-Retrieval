import os.path
import whoosh.reading
from whoosh import index
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.query import *
import json
import re

number_of_returned_results = 10 # Adjustable variable for returned results

def CreateDB(): # Initialize and populate database
    outfile = open("testoutput.txt", "w")
    # Create custom schema for database
    schema = Schema(title=ID(stored=True), content=TEXT(stored=True))
    ix = index.create_in("indexdir", schema)
    ix = index.open_dir("indexdir")
    writer = ix.writer()
    # Import and generate database
    with open("crawled_websites.json") as f:
        data = json.load(f)
    for url in data:
        writer.add_document(title=url, content=data[url])
    writer.commit()
    with ix.reader() as reader:
        '''
        for item in reader.all_terms():
            outfile.write(item)
        '''
        print("Test:")
        inc = 0
        doc_freq_list = []
        for item in reader.all_terms():
            if inc == 300:
                break
            term = item[1].decode("utf-8")
            #print(term, reader.frequency('content', term))
            m = reader.postings("content", term)
            print(term, end=': ')
            for i in m.all_ids():
                doc_freq_list.append(i)
            for doc in doc_freq_list:
                print(doc, end=" ")
            print()
            doc_freq_list.clear()
            #print(term, reader.weight("content", term))
            inc += 1
        
        
        #for item in reader.all_terms():
            
        '''
        # This prints out all the terms
        if item[0] == 'content':
            print(item[1])
        '''
        #outfile.write('\n'.join(str(item) for item in reader.all_terms()))
    outfile.close()
    return ix

def Search(ix, number_of_returned_results): # Searching functionality
    inp = '' # Variable to accept input from user for searches
    with ix.searcher() as searcher:
        parser = QueryParser("content", ix.schema)
        print("\nType words to search or 'exit' to exit the program")
        while True:
            while not inp:
                inp = input("Enter search term(s): ")
            if inp == "exit":
                print('Exiting program...')
                exit()
            query = parser.parse(inp)
            results = searcher.search(query, limit=number_of_returned_results)
            print(results)
            ans = input("Display ranked results, y/n? ")
            if ans == 'y':
                if not results: print("There were no results found!")
                else:#print(f"Result: {results[0]}")
                    for hit in results:
                        print(hit["title"])
                        print(hit.highlights("content"))
            inp = '' # Reset input variable for searching
            
def main():
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    ix = CreateDB()
    #Search(ix, number_of_returned_results)
    
if __name__ == "__main__":
    main()
