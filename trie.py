class Trie:
    def __init__(self):
        self.root = {}

    def add_word(self,word):
        """
        Adds given word to Trie
        """
        curr = self.root
        for ch in word:
            if(ch not in curr):
                curr[ch]={}
            curr=curr[ch]
        curr["*"]="*"

    def find_word(self,word):
        """
        Find a word in Trie
        """
        curr = self.root
        for ch in word:
            if(ch not in curr):
                return False
            curr=curr[ch]
        if("*" in curr):
            return True
        else:
            return False

    def delete_word(self,word):
        """
        Delete Word from Trie
        """
        curr = self.root
        stack=[]
        for ch in word:
            if(ch not in curr):
                return False
            curr=curr[ch]
            stack.append((ch,curr))

        if("*" in curr):
            del curr["*"]
            while(stack):
                ch,childs=stack.pop()
                if(childs=={}):
                    pch,pchilds=stack.pop()
                    del pchilds[ch]
                    stack.append((pch,pchilds))
        else:
            return False

    def prefix_words(self,prefix):
        """
        Lists all words in Trie with given prefix
        """
        words=[]
        curr = self.root
        char = ""
        for ch in prefix:
            if(ch in curr):
                char,curr=ch,curr[ch]

            else:
                break
        else:
            words=self.__list_words(curr)
            # words = list(map(lambda x: prefix+x , self.__list_words(curr)))
            words=list(filter(lambda x: x!="", words))
        return words


    def  __list_words(self,root):
        words = []
        for k, v in root.items():
            if k != '*':
                for el in self.__list_words(v):
                    words.append(k + el)
            else:
                words.append('')
        return words

    def show(self):
        print(self.__list_words(self.root))




print('a'>'A')