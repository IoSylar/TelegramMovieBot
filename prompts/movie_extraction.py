from pydantic import BaseModel

class MovieExtraction(BaseModel):

    template: str = """
        Dato il seguente testo estrai il nome dei film mezionati\n\n
        Dovrai restituire una array di nomi di film e NIENTE ALTRO, ad esempio: Puoi guardare Scarface oppure Quei bravi ragazzi
        output:
        [Scarface,Quei bravi ragazzi]
        Oppure ad esempio: Puoi guardare La casa di carta è un bel film
        output:
        [La casa di carta]
        Classify:
        {input_text}
    """

    input_text: str

    def __str__(self):

        return self.template.format(input_text = self.input_text)