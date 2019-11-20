"""
Get the changes between two versions of a paper
"""
import diff_match_patch as diff
import difflib


dmp = diff.diff_match_patch()

def dif_paper(paper1, paper2):
    """get differences between two papers for each section separatly using diff_math_patch """
    difference = []
    for t1, t2 in zip(paper1['sections'], paper2['sections']):
        dif = dmp.diff_main(t1['text'], t2['text'])
        dmp.diff_cleanupSemantic(dif)
        
        for i in dif:
            if i[0] != 0:
                difference.append(i)
    return difference

def dif_paper_append(paper1, paper2):
     """get differences between two papers, converting them both to one string using diff_math_patch"""
    text1 = paper_to_text(paper1)
    text2 = paper_to_text(paper2)
        
    dif = dmp.diff_main(text1, text2)
    dmp.diff_cleanupSemantic(dif)
    difference = []
    for i in dif:
            if i[0] != 0:
                difference.append(i)
    return difference

def dif_paper_append_2(paper1, paper2):
    """get differences between two papers, converting them both to one string using difflib"""
    text1 = paper_to_text(paper1)
    text2 = paper_to_text(paper2)
        
    text1 = text1.split('. ')
    text2 = text2.split('. ')
    d = difflib.Differ()
    dif = d.compare(text1, text2)
    
    difference = []
    
    for i in dif:
        if i[0] in '-+':
            difference.append(i)
    
    return difference

def paper_to_text(paper):
    """append the sections of a paper to one string"""
    text = ''
    for section in paper['sections']:
        text += section['heading']
        text += '\n'
        text += section['text']
        text += '\n'
    return text
