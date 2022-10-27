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
    # Create custom schema for database
    schema = Schema(title=ID(stored=True), content=TEXT(stored=True))
    ix = index.create_in("indexdir", schema)
    ix = index.open_dir("indexdir")
    writer = ix.writer()
    # Import and generate database
    with open("crawled_websites.json", encoding="utf-8") as f:
        data = json.load(f)
    for url in data:
        writer.add_document(title=url, content=data[url])
    writer.commit()
    return ix

def InvertedIndexBuilder(ix):
    with open("inverted_index.txt", "w", encoding="utf-8") as outfile:
        with ix.reader() as reader:
            freq_list = []
            space = " "
            for item in reader.all_terms():
                if item[0] == "content":
                    term = item[1].decode("utf-8")
                    m = reader.postings("content", term)
                    term += ": "
                    outfile.write(term)
                    for doc in m.all_ids():
                        freq_list.append(doc)
                    for doc in freq_list:
                        outfile.write(str(doc))
                        outfile.write(space)
                    outfile.write("\n")
                    freq_list.clear()

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
    #InvertedIndexBuilder(ix)
    Search(ix, number_of_returned_results)
    
if __name__ == "__main__":
    main()
