from links import RemoteLinks
import file_management
import web_data
import threading
import sys

def downloadExamSection(currentPath, examClass):
    '''
    used for multithreaded downloading.
    '''
    test = []
    sectionPath = file_management.createFolder(currentPath, examClass.name)
    seasonExams = web_data.getExamSeasons(examClass.url)
    for seasonExam in seasonExams:
        seasonPath = file_management.createFolder(sectionPath, seasonExam.name)
        exams = web_data.getExams(seasonExam.url)
        test.append(exams)
        file_management.populateFolders(seasonPath, exams)
    sys.exit()

def downloadCAIE(folderName, pattern, url, syllabusCode):
    '''
    downloads a caie exam.
    '''
    currentPath = file_management.createFolder('output', folderName)
    examClasses = web_data.getExamClasses(url, syllabusCode)
    
    if syllabusCode.lower() == 'all':
        for examClass in examClasses:
            processThread = threading.Thread(
                target=downloadExamSection, args=(currentPath, examClass))
            processThread.start()
    else:
        # fix: extract the specific object from the array wrapper using [0]
        examClassList = list(filter(lambda x: syllabusCode in x.name, examClasses))
        if len(examClassList) > 0:
            examClass = examClassList[0]
            print(f"match found: {examClass.name}")
            downloadExamSection(currentPath, examClass)

def printDivider():
    bar = '-' * 50
    print()
    print(bar)
    print('*' * 50)
    print(bar)
    print()

def downloadAICE(syllabusCode):
    downloadCAIE('AS and A Levels', RemoteLinks.AICE_PATTERN.value,
                 RemoteLinks.AICE.value, syllabusCode)

def downloadIGCSE(syllabusCode):
    downloadCAIE('IGCSEs', RemoteLinks.IGCSE_PATTERN.value,
                 RemoteLinks.IGCSE.value, syllabusCode)

def downloadO(syllabusCode):
    downloadCAIE('O Levels', RemoteLinks.O_PATTERN.value,
                 RemoteLinks.O.value, syllabusCode)

def listClasses(value, pattern):
    exams = web_data.getExamClasses(value, pattern)
    printDivider()
    for exam in exams:
        print(exam.name)
    printDivider()

def listAICE():
    listClasses(RemoteLinks.AICE.value, RemoteLinks.AICE_PATTERN.value)

def listIGCSE():
    listClasses(RemoteLinks.IGCSE.value, RemoteLinks.IGCSE_PATTERN.value)

def listO():
    listClasses(RemoteLinks.O.value, RemoteLinks.O_PATTERN.value)