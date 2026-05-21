import os
import re
import json
import unicodedata
import pyperclip
import traceback
from lxml import etree

ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

class ProcessingMemory:
    # Chemin du fichier dictionnaire
    DICT_FILE = r"corrections_dict.json"
    LEXIQUE_FILE = r"lexique.json"
    lexique_json = None
    lexique = None
    dictionary = None
    dictionary_json = None

    usedCorrectionKeys = set()

    def add_to_lexique(self, word):
        word = unicodedata.normalize('NFC', word)
        self.lexique_json.append(word)
        self.lexique.add(word)

    def add_to_dictionary(self, original, corrected):
        """Add a new correction to the dictionary."""
        original = unicodedata.normalize('NFC', original)
        corrected = unicodedata.normalize('NFC', corrected)

        if original not in self.dictionary['corrections']:
            self.dictionary['corrections'][original] = corrected
            self.dictionary_json['corrections'][original] = corrected
            print(f"Ajouté au dictionnaire: {original} -> {corrected}")
            self.add_phrase_to_runtime_ignored(corrected)
        else:
            print(f"{original} est déjà dans le dictionnaire avec la correction {self.dictionary['corrections'][original]}")

    def add_phrase_to_runtime_ignored(self, phrase):
        """Add a phrase to the runtime ignored list."""
        phrase = unicodedata.normalize('NFC', phrase)
        phrase = phrase.strip()
        words = phrase.split()
        for word in words:
            self.dictionary['ignored'].add(word)

    def find_word(self,word):
        word = unicodedata.normalize('NFC', word)
        if word in self.dictionary['corrections']:
            return self.dictionary['corrections'][word]
        if word in self.dictionary['ignored']:
            return word
        if word in self.dictionary['foreign_words']:
            return word
        if word in self.lexique:
            return word
        return False
    
    def add_to_ignored(self, word):
        """Add a word to the ignored list."""
        word = unicodedata.normalize('NFC', word)

        if word not in self.dictionary['ignored']:
            self.dictionary['ignored'].add(word)
        if(word not in self.dictionary_json['ignored']):
            self.dictionary_json['ignored'].append(word)
            print(f"Mot '{word}' ajouté à la liste d'ignorés")
        else:
            print(f"{word} est déjà dans la liste d'ignorés")

    def add_to_skipped(self, word):
        """Add a word to the skipped list."""
        word = unicodedata.normalize('NFC', word)

        if word not in self.dictionary['skipped']:
            self.dictionary['skipped'].add(word)
            self.dictionary_json['skipped'].append(word)
            print(f"Mot '{word}' ajouté à la liste de skipped")
        else:
            print(f"{word} est déjà dans la liste de skipped")

    def add_to_foreign_words(self, word):
        """Add a word to the foreign words list."""
        word = unicodedata.normalize('NFC', word)

        if word not in self.dictionary['foreign_words']:
            self.dictionary['foreign_words'].add(word)
            self.dictionary_json['foreign_words'].append(word)
            print(f"Mot '{word}' ajouté à la liste de foreign words")
        else:
            print(f"{word} est déjà dans la liste de foreign words")

    def initialize_dictionary(self):
        """Initialize the correction dictionary and lexique."""
        # Charger le dictionnaire et le lexique depuis les fichiers JSON
        self.dictionary_json = self.load_dictionary()
        self.lexique_json = self.load_lexique()

        # Normaliser la liste d'ignorés
        normalized_ignored = {unicodedata.normalize('NFC', word) for word in self.dictionary_json['ignored']}
        normalized_skipped = {unicodedata.normalize('NFC', word) for word in self.dictionary_json['skipped']}
        normalized_foreign_words = {unicodedata.normalize('NFC', word) for word in self.dictionary_json['foreign_words']}
        # Normaliser les corrections (clés et valeurs)
        normalized_corrections = {}
        for key, value in self.dictionary_json['corrections'].items():    
            normalized_key = unicodedata.normalize('NFC', key)
            normalized_value = unicodedata.normalize('NFC', value)
            normalized_corrections[normalized_key] = normalized_value

        # Normaliser le lexique
        normalized_lexique = {unicodedata.normalize('NFC', word) for word in self.lexique_json}

        self.dictionary = {
            'corrections': normalized_corrections,
            'ignored': normalized_ignored,
            'foreign_words': normalized_foreign_words,
            'skipped': normalized_skipped
        }
        self.lexique = normalized_lexique

        for word in normalized_corrections.values():
            self.add_phrase_to_runtime_ignored(word)

    def load_dictionary(self):
        """Load correction dictionary from JSON file."""
        if os.path.exists(self.DICT_FILE):
            try:
                with open(self.DICT_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data
            except Exception as e:
                print(f"Erreur lors du chargement du dictionnaire: {e}")
                return None
        return {'corrections': {}, 'ignored': [], 'foreign_words': [], 'skipped': []}
    
    def load_lexique(self):
        """Load lexique from JSON file."""
        if os.path.exists(self.LEXIQUE_FILE):
            try:
                with open(self.LEXIQUE_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('lexique', [])
            except Exception as e:
                print(f"Erreur lors du chargement du lexique: {e}")
        return []

    def save_dictionary(self):
        """Save correction dictionary to JSON file."""
        try:
            with open(self.DICT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.dictionary_json, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du dictionnaire: {e}")

class CorpusProcessor:
    memory = None
    replacement_enabled = False
    endOfLineAutoDected = False
    countMode = False
    interactive_mode=True
    ShouldConverteUnusedDesaglutinationToIgnored=False
    OnlyTestFile=False

    def detect_all_words(self,text,noduplicates=True):
        """Detect all words in the text for comprehensive review."""
        if not text:
            return []
        
        # Normaliser le texte pour gérer les caractères composés
        normalized_text = unicodedata.normalize('NFC', text)
        
        # Séparer par les espaces et caractères de ponctuation sauf apostrophe
        # Liste explicite des caractères de séparation (ponctuation, espaces, etc.)
        split_chars = " \t\n\r.,;:!?()[]{}<>«»\"“”‘’_/\\|@#$%^&*+=~`…·•©®°§†‡¶"
        # Construire une expression régulière qui sépare sur ces caractères
        pattern = "[" + re.escape(split_chars) + "]+"
        words = re.split(pattern, normalized_text)
        # Filtrer les mots vides et ne garder que ceux avec des lettres
        words = [word for word in words if word and re.search(r'[a-zA-ZàâäéèêëïîôöùûüÿçñãẽĩõũÃẼĨÕŨÑ¬\u0303]', word)]
        if(noduplicates):
            return list(set(words))  # Supprimer les doublons
        return words

    def apply_dictionary_corrections(self,text, dictionary, regWords):
        """Apply dictionary corrections to text."""
        if not text or not dictionary.get('corrections'):
            return text
        text = unicodedata.normalize('NFC', text)
        for word in regWords:
            normalized_word = unicodedata.normalize('NFC', word)
            if normalized_word in dictionary['corrections']:
                corrected = dictionary['corrections'][normalized_word]
                self.memory.usedCorrectionKeys.add(normalized_word)
                # Remplacement exact des mots (avec limites de mots)
                text = re.sub(r'\b' + re.escape(word) + r'\b', corrected, text, flags=re.UNICODE)
        # for original, corrected in dictionary['corrections'].items():
        #     # Remplacement exact des mots (avec limites de mots)
        #     text = re.sub(r'\b' + re.escape(original) + r'\b', corrected, text, flags=re.IGNORECASE)
        
        return text

    def get_word_context(self,text, word, context_words=5):
        """Get context around a word (few words before and after)."""
        if not text or not word:
            return ""
        
        # Normaliser le texte pour gérer les caractères composés
        normalized_text = unicodedata.normalize('NFC', text)
        normalized_word = unicodedata.normalize('NFC', word)
        
        # Séparer par les espaces et caractères de ponctuation sauf apostrophe
        # Liste explicite des caractères de séparation (ponctuation, espaces, etc.)
        split_chars = " \t\n\r.,;:!?()[]{}<>«»\"“”‘’_/\\|@#$%^&*+=~`…·•©®°§†‡¶"
        # Construire une expression régulière qui sépare sur ces caractères
        pattern = "[" + re.escape(split_chars) + "]+"
        words = re.split(pattern, normalized_text)
        words = [w for w in words if w and re.search(r'[a-zA-ZàâäéèêëïîôöùûüÿçñãẽĩõũÃẼĨÕŨÑ\u0303]', w)]
        contexts = []
        
        for i, w in enumerate(words):
            if w.lower() == normalized_word.lower():
                start = max(0, i - context_words)
                end = min(len(words), i + context_words + 1)
                context = ' '.join(words[start:end])
                # Mettre le mot en évidence
                context = context.replace(w, f"[{w}]")
                contexts.append(context)
        
        return ' | '.join(contexts) if contexts else ""

    def isUnknownWord(self, word,checkSkipped=True):
        """Check if a word is in the known words list."""
        normalized_word = unicodedata.normalize('NFC', word)
        isUnknown=normalized_word not in self.memory.dictionary['corrections'] and \
            normalized_word not in self.memory.dictionary['ignored'] and \
            normalized_word not in self.memory.dictionary['foreign_words'] and \
            normalized_word not in self.memory.lexique
        if(checkSkipped):
            isUnknown=isUnknown and normalized_word not in self.memory.dictionary['skipped']
        return isUnknown

    def prompt_for_corrections(self, problematic_words, all_texts, current_reg, total_regs):
        """Prompt user to add corrections for problematic words."""
        new_corrections = False
        new_ignored = False
        found_something=False
        for word in problematic_words:
            # Normaliser le mot pour les comparaisons
            normalized_word = unicodedata.normalize('NFC', word)
            
            # Vérifier si le mot est dans les corrections ou dans la liste d'ignorés
            if self.isUnknownWord(normalized_word):
                if not found_something:
                    found_something=True
                    print(f"\nDans reg {current_reg}/{total_regs}")
                if(self.countMode):
                    self.memory.add_to_lexique(normalized_word)
                    continue
                # Chercher le contexte dans tous les textes
                context = ""
                for text in all_texts:
                    word_context = self.get_word_context(text, normalized_word)
                    if word_context:
                        context = word_context
                        break
                
                # Affichage du mot avec information sur sa composition Unicode
                print(f"\nMot détecté: '{normalized_word}'")
                # Afficher la décomposition Unicode pour debug
                decomposed = unicodedata.normalize('NFD', normalized_word)
                if decomposed != normalized_word:
                    print(f"Composition Unicode: {[unicodedata.name(c, 'UNKNOWN') for c in decomposed]}")
                
                if context:
                    print(f"Contexte: ...{context}...")
                aglutinations= self.detect_potential_aglutination(normalized_word)
                response = input(f"Correction pour '{normalized_word}'? (o=oui/n=non/i=ignorer/l=etrangé/q=quitter/s=skip): ").lower()
                if response.isdigit():
                    index = int(response)
                    if 0 <= index < len(aglutinations):
                        print(f"Vous avez sélectionné: {aglutinations[index]}")
                        self.memory.add_to_dictionary(normalized_word, aglutinations[index])
                        new_corrections = True
                elif response == 'o':
                    pyperclip.copy(normalized_word)
                    correction = input(f"Correction pour '{normalized_word}': ")
                    if correction.strip():
                        self.memory.add_to_dictionary(normalized_word, correction.strip())
                        new_corrections = True
                elif response == 'i':
                    self.memory.add_to_ignored(normalized_word)
                    new_ignored = True
                elif response == 'q':
                    print("Arrêt de l'ajout de corrections, continuation du script...")
                    self.interactive_mode = False
                    break
                elif response == 'count':
                    self.countMode = True
                    continue
                elif response == 's':
                    self.memory.add_to_skipped(normalized_word)
                    new_ignored = True
                    continue
                elif response == 'l':
                    self.memory.add_to_foreign_words(normalized_word)
                    new_ignored = True
                    continue
        
        return bool(new_corrections or new_ignored)
    
    def detect_potential_aglutination(self, word):
        results = []
        
        if len(word) >= 4:
            for i in range(2,len(word)-1):
                word1 = word[:i]
                word2 = word[i:]
                word1coorect=self.memory.find_word(word1)
                word2coorect=self.memory.find_word(word2)
                if word1coorect!=False and word2coorect!=False:
                    if word1coorect[-1]=="'":
                        self.add_to_suggestion([word1coorect, word2coorect], word1coorect + word2coorect, results)
                    else:
                        self.add_to_suggestion([word1coorect, word2coorect], word1coorect + " " + word2coorect, results)
                else:
                    continue
        if len(word) >=6:
            for i in range(2,len(word) - 1-2):
                for j in range(i+2, len(word) - 1):
                    word1 = word[:i]
                    word2 = word[i:j]
                    word3 = word[j:]
                    word1coorect=self.memory.find_word(word1)
                    word2coorect=self.memory.find_word(word2)
                    word3coorect=self.memory.find_word(word3)
                    if word1coorect!=False and word2coorect!=False and word3coorect!=False:
                        suggestion=word1coorect
                        if word1coorect[-1]=="'":
                            suggestion += word2coorect
                        else:
                            suggestion += " " + word2coorect
                        
                        if word2coorect[-1]=="'":
                            suggestion += word3coorect
                        else:
                            suggestion += " " + word3coorect

                        self.add_to_suggestion([word1coorect, word2coorect, word3coorect], suggestion , results)

                    else:
                        continue
        return results
    
    def add_to_suggestion(self,words,suggestion,results):
        if suggestion not in results:
            results.append(suggestion)
            wordsstr = " + ".join(words)
            print(f"{len(results)-1}:Potentiel agglutination détecté: {wordsstr} = {results[-1]}")

    def remove_special_characters(self, text):
        """Remove specific characters like 'ſ' and '¬' from text."""
        if not text:
            return text
        return text.replace('ſ', 's').replace('ß', 'ss').replace('’', "'").replace('‘', "'").replace("   ", " ").replace("  ", " ").replace("  ", " ")#.replace('¬', '')

    def check_end_line_split(self,nouveau_texte,reg_elements,current_reg_index):
        processLineSplit=nouveau_texte.endswith('¬')
        processAutoDetectLineSplit=False
        wordExistWithoutDash=False
        next_reg_index=-1
        nextLineWords=None
        if(not processLineSplit and self.endOfLineAutoDected):
            # if( nouveau_texte.endswith('-')):
            #     processAutoDetectLineSplit=True
            # else:
                next_reg_index=self.GetNextRegIndex(reg_elements,current_reg_index)
                if(next_reg_index>0):
                    nextLineWords=self.detect_all_words(reg_elements[next_reg_index].text,False)
                    selfLineWords=self.detect_all_words(nouveau_texte,False)
                    if(len(nextLineWords)>0 and len(selfLineWords)>0):
                        lastWord=self.remove_special_characters(selfLineWords[-1])
                        firstWord=self.remove_special_characters(nextLineWords[0])
                        lastWordIsUnknown=self.isUnknownWord(lastWord,False)
                        firstWordIsUnknown=self.isUnknownWord(firstWord,False)
                        if(lastWordIsUnknown or (firstWordIsUnknown and not (firstWord.endswith("-") or firstWord.endswith("¬")))):
                            if(not self.isUnknownWord(lastWord+firstWord,False)):
                                processAutoDetectLineSplit=True
                            elif(lastWord.endswith("-")):
                                    if(not self.isUnknownWord(lastWord[:-1]+firstWord)):
                                        processAutoDetectLineSplit=True
                                        wordExistWithoutDash=True
                            else:
                                print(f"newword ? {lastWord}+{firstWord} = {lastWord+firstWord} in reg {current_reg_index} and {next_reg_index}")
                        elif(False and not lastWordIsUnknown and not firstWordIsUnknown and not self.isUnknownWord(lastWord+firstWord,False)):
                                print(f"potential split word ? {lastWord}+{firstWord} in reg {current_reg_index} and {next_reg_index}")

        if(processLineSplit or processAutoDetectLineSplit):
            next_reg_index=next_reg_index if next_reg_index>0 else self.GetNextRegIndex(reg_elements,current_reg_index)
            if(next_reg_index>0):
                nextLineWords= nextLineWords if nextLineWords!=None else self.detect_all_words(reg_elements[next_reg_index].text,False)
                if(len(nextLineWords)<=0):
                    print(f"Erreur de détection du mot après coupure de ligne pour le reg {current_reg_index}: {reg_elements[next_reg_index].text}")
                    return nouveau_texte
                reg_elements[next_reg_index].text=unicodedata.normalize('NFC', reg_elements[next_reg_index].text)
                reg_elements[next_reg_index].text=reg_elements[next_reg_index].text.replace(nextLineWords[0],"",1)
                if(nouveau_texte.endswith('-') and wordExistWithoutDash):
                    nouveau_texte=nouveau_texte[:-1]
                nouveau_texte=nouveau_texte.replace('¬','')+nextLineWords[0]

                ponctuationARemonter=[",",":",".",")","!","?"]
                
                for char in ponctuationARemonter:
                     if(reg_elements[next_reg_index].text.startswith(" "+char)):
                        nouveau_texte+=reg_elements[next_reg_index].text[:2]
                        reg_elements[next_reg_index].text=reg_elements[next_reg_index].text[2:]
                        break
                for char in ponctuationARemonter:   
                    if(reg_elements[next_reg_index].text.startswith(char)):     
                        nouveau_texte+=reg_elements[next_reg_index].text[:1]
                        reg_elements[next_reg_index].text=reg_elements[next_reg_index].text[1:]
                        break

                reg_elements[next_reg_index].text=reg_elements[next_reg_index].text.strip()
        return nouveau_texte

    def GetNextRegIndex(self,reg_elements,current_reg_index):
        current_reg_parent = reg_elements[current_reg_index].getparent().getparent()
        # Ignorer les QuireMarksZone elle n'ont pas besoin d'être matché
        if("QuireMarksZone".lower() in current_reg_parent.get("type","").lower()):
            return -1
        
        source_is_main= "mainzone" in current_reg_parent.get("type","").lower()
        
        next_index=current_reg_index +1
        if(next_index>=len(reg_elements)):
            print(f"can't find next reg for last reg")
            return -1
        next_reg_parent = reg_elements[next_index].getparent().getparent()
        next_is_main= "mainzone" in next_reg_parent.get("type","").lower()
        
        while(next_is_main!=source_is_main):
            #print(f"reg zone error ({current_reg_parent.get("type","")}/{next_reg_parent.get("type","")}) look for type arround {reg_elements[current_reg_index].text}")
            next_index=next_index+1
            if(next_index>=len(reg_elements)):
                print(f"reg zone error ({current_reg_parent.get("type","")}/end of reg) look for type arround {reg_elements[current_reg_index].text}")
                return -1
            next_reg_parent = reg_elements[next_index].getparent().getparent()
            next_is_main= "mainzone" in next_reg_parent.get("type","").lower()
       
        if(next_is_main==source_is_main):
            return next_index
        else:
            print(f"reg zone error ({current_reg_parent.get("type","")}/{next_reg_parent.get("type","")}) look for type arround {reg_elements[current_reg_index].text}")

            return-1
        
    def process_reg_elements(self, root):
        """Process all <reg> elements in the XML tree."""
        change = False
        reg_elements = root.findall('.//tei:reg', namespaces=ns)
        current_reg = -1
        total_regs = len(reg_elements)
        for reg in reg_elements:
            current_reg += 1
            if reg.text:
                all_problematic_words = []
                all_texts = []  # Stocker tous les textes pour le contexte
                regWords=None            
                nouveau_texte = self.remove_special_characters(reg.text)
                nouveau_texte =self.check_end_line_split(nouveau_texte,reg_elements,current_reg)
                nouveau_texte = self.remove_special_characters(nouveau_texte)
                all_texts.append(nouveau_texte)
                

                problematic_words = self.detect_all_words(nouveau_texte)
                regWords = problematic_words
               
                
                all_problematic_words.extend(problematic_words)

                if self.replacement_enabled:
                    if regWords is None:
                        regWords=self.detect_all_words(nouveau_texte)
                    # Appliquer les corrections du dictionnaire
                    nouveau_texte = self.apply_dictionary_corrections(nouveau_texte, self.memory.dictionary, regWords)
                
                if nouveau_texte != reg.text:
                    reg.text = nouveau_texte
                    change = True
        
                # Proposer d'ajouter des corrections si en mode interactif
                if (self.interactive_mode or self.countMode) and all_problematic_words:
                    unique_words = list(set(all_problematic_words))
                        
                    if self.prompt_for_corrections(unique_words, all_texts,current_reg,total_regs):
                        self.memory.save_dictionary()

        return change

    def process_xml_file(self, chemin_fichier, chemin_fichier_output):
        """Process a single XML file and return True if modifications were made."""
        try:
            parser = etree.XMLParser(remove_blank_text=False)
            tree = etree.parse(chemin_fichier, parser)
            root = tree.getroot()

            change = self.process_reg_elements(root)

            if change:
                tree.write(chemin_fichier_output, pretty_print=True, encoding="utf-8", method="xml")
                return True
            return False
        except Exception as e:
            print(f"Erreur avec {os.path.basename(chemin_fichier)} : {e}")
            print(f"Traceback : {traceback.format_exc()}")
            return False

    def process_corpus(self, dossier_corpus, dossier_corpus_output):
        """Process all XML files in the corpus directory."""
        self.memory = ProcessingMemory()
        self.memory.initialize_dictionary()
        lcount = len(self.memory.lexique)
        modifies = 0
        
        if self.endOfLineAutoDected:
            print("Mode détection de fin de ligne activé: les mots suivis d'un '¬'ou '-' skipped seront potentiellement corrigés")
            print("les mots de find de phrase ou debut de phrase qui ne sont pas dans le lexique ou les corrections seront aussi potentiellement corrigés par un raprochement de fin de phrase")
        
        for nom_fichier in os.listdir(dossier_corpus):
            if(not self.OnlyTestFile or nom_fichier=="test.xml"):
                if nom_fichier.endswith(".xml"):
                    chemin_fichier = os.path.join(dossier_corpus, nom_fichier)
                    chemin_fichier_output = os.path.join(dossier_corpus_output, nom_fichier)
                    print(f"Traitement du fichier : {nom_fichier}")
                    if self.process_xml_file(chemin_fichier, chemin_fichier_output):
                        modifies += 1

        print(f"corrections: {len(self.memory.dictionary['corrections'])}, ignored: {len(self.memory.dictionary['ignored'])}, left: {len(self.memory.lexique)-lcount}")
        if self.ShouldConverteUnusedDesaglutinationToIgnored:
           self.ConverteUnusedDesaglutinationToIgnored()
        return modifies

    def ConverteUnusedDesaglutinationToIgnored(self):
        """Convert unused desaglutination suggestions to ignored words."""
        for key, value in self.memory.dictionary['corrections'].items():
            if key not in self.memory.usedCorrectionKeys:
                correction = self.memory.dictionary['corrections'][key]
                correction = unicodedata.normalize('NFC', correction)
                correction = correction.strip()
                words = correction.split()
                if(len(words)>1):
                    for word in words:
                        self.memory.add_to_ignored(word)
                    self.memory.dictionary_json['corrections'].pop(key, None)
                    print(f"Correction non utilisée convertie en ignoré: {key} -> {correction}")
        self.memory.save_dictionary()
def main():
    """Main function to execute the text processing."""
    dossier_corpus = r"origreg"
    #dossier_corpus=os.path.realpath(dossier_corpus)
    dossier_corpus_output = r"normalized"
    print(os.path.realpath(dossier_corpus))
    corpusProcessor = CorpusProcessor()
    # Demander le mode de détection
    mode_choice = input("Mode de détection de fin de ligne (1=actif, 2=inactif) /!\\ à n'activer que si le text est deja normalisé/!\\: ").strip()
    corpusProcessor.endOfLineAutoDected = mode_choice == "1"
    mode_choice = input("Mode avancé (1=actif, 2=inactif): ").strip()
    if(mode_choice == "1"):
        mode_choice = input("Mode de conversion des désaglutinations non utilisées (1=actif, 2=inactif): /!\\ commit dictionary /!\\: ").strip()
        corpusProcessor.ShouldConverteUnusedDesaglutinationToIgnored = mode_choice == "1"
        mode_choice = input("Only Test File (1=actif, 2=inactif): ").strip()
        corpusProcessor.OnlyTestFile = mode_choice == "1"
    mode_choice = input("Mode de remplacement (1=actif, 2=inactif): ").strip()
    corpusProcessor.replacement_enabled = mode_choice == "1"

    modifies = corpusProcessor.process_corpus(dossier_corpus, dossier_corpus_output)
    print(f"Traitement terminé : {modifies} fichiers modifiés (suppression 'ſ' et '¬' dans <reg>).")

if __name__ == "__main__":
    main()
    # Test pour comprendre le problème
    # word = "negociatiõs"
    # print(f"Mot: '{word}'")
    # print(f"Longueur: {len(word)}")
    # print(f"Codes Unicode: {[ord(c) for c in word]}")
    # print(f"NFD: {repr(unicodedata.normalize('NFD', word))}")
    # print(f"NFC: {repr(unicodedata.normalize('NFC', word))}")

    # # Test du pattern

    # text = ", negociatiõs, "
    # pattern = r'\b' + re.escape(word) + r'\b'
    # print(f"Pattern: {pattern}")
    # print(f"Match: {re.search(pattern, text)}")
    # print(f"Match avec UNICODE: {re.search(pattern, text, re.UNICODE)}")
