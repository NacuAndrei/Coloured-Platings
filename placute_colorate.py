import os
import queue
import sys
import copy
import time
import stopit


class NodParcurgere:
	def __init__(self, info, parinte, cost, h):
		self.info = info
		self.parinte = parinte
		self.g = cost
		self.h = h
		self.f = self.g + self.h

	def __lt__(self, dr):
		if self.f < dr.f:
			return True
		if self.f == dr.f and self.g < dr.g:
			return True
		return False

	def __eq__(self, dr):
		return self.f == dr.f and self.g == dr.g

	def obtineDrum(self):
		l = [self]
		nod = self
		while nod.parinte is not None:
			l.insert(0, nod.parinte)
			nod = nod.parinte
		return l

	def afisDrum(self):
		l = self.obtineDrum()
		for i, nod in enumerate(l):
			f.write('\n')
			f.write(str(i+1) + ")\n")
			for linie in nod.info:
				f.write(str(linie) + '\n')

		f.write("\nCost: " + str(self.g))
		f.write("\nLungime: " + str(len(l)))

		return len(l)

	def contineInDrum(self, infoNodNou):
		nodDrum = self
		while nodDrum is not None:
			if infoNodNou == nodDrum.info:
				return True
		return False

	def __repr__(self):
		sir = ""
		sir += str(self.info)
		return sir


class Graph:
	def __init__(self, nume_fisier):
		f = open(nume_fisier, "r")
		self.k = 0
		try:
			self.k = int(f.readline())
		except ValueError:
			sys.exit("\nk trebuie sa fie un numar! Eroarea are loc in fisierul: " + nume_fisier)

		sirFisier = f.read()
		listaLinii = sirFisier.strip().split("\n")
		self.N = len(listaLinii)					#: dimensiunile matricei
		self.M = len(listaLinii[0])

		self.start = []
		self.dictFrecventaStart = {}				#: dictionar pentru frecventa fiecarei culori

		for linie in listaLinii:
			self.start.append([value for value in linie.strip()])
			for value in linie:
				if (value.isalpha() == 0 or value.isupper()) and value != '#':		#: exceptie pentru datele introduse gresit in fisier
					sys.exit("\nPatratica ''" + value + "'' nu este o litera sau este litera mare! Eroarea are loc in fisierul: "
							 + nume_fisier + "\nProgramul si-a finalizat executia fara succes :(\n")

				if value != '#':
					if value in self.dictFrecventaStart:
						self.dictFrecventaStart[value] += 1
					else:
						self.dictFrecventaStart[value] = 1

		self.scopuri = [[['#'] * self.M] * self.N]

	def testeaza_scop(self, nodCurent):
		return nodCurent.info in self.scopuri

	def nuAreSolutii(self):
		"""
			Nu am solutie cand nu am macar k patratele de aceeasi culoare.

        Returns:
            True if successful, False otherwise.

        """
		for key, value in self.dictFrecventaStart.items():
			if value < self.k:
				return 0
		return 1

	def frecventa(self, nodCurent):
		"""
			Genereaza un dictionar ce retine cate patratele apartin unei culori.

		Args:
		       nodCurent (NodParcurgere): Nodul(starea) curenta din graful generat.

        Returns:
            dictFrecventa

        """
		dictFrecventa = {}
		for i in range(self.N):
			for j in range(self.M):
				if nodCurent.info[i][j] != '#':
					if nodCurent.info[i][j] in dictFrecventa:
						dictFrecventa[nodCurent.info[i][j]] += 1
					else:
						dictFrecventa[nodCurent.info[i][j]] = 1
		return dictFrecventa

	def umple_matriceId(self, nodCurent, matriceId):
		"""
			Construieste o matrice de id-uri pentru fiecare piesa unica.
			Verific patratica din stanga sau deasupra valorii curente (cand pot).
			Cazul in care doua piese initial unice se dovedesc a fi aceeasi piesa
			este rezolvat cu reparcurgerea matricei si schimbarea id-urilor maxime
			cu id-urile minime(a doua parte din piesa ia id-ul primei parti).
			Nu este garantat ca id-urile sunt consecutive.
			idMax reprezinta cel mai mare id din matrice.

		   Args:
		       nodCurent (NodParcurgere): Nodul(starea) curenta din graful generat.
		       matriceId (list): O matrice de id-uri ce reprezinta fiecare piesa unica,
		       unde culoarea nu conteaza.

		   Returns:
		       matriceId
		       idMax

		   """

		idMax = 0
		for i in range(self.N):
			for j in range(self.M):
				if nodCurent.info[i][j] != '#':
					if j != 0 and nodCurent.info[i][j] == nodCurent.info[i][j-1]:
						matriceId[i][j] = matriceId[i][j-1]
						if i != 0 and nodCurent.info[i][j] == nodCurent.info[i-1][j]:
							zonaMax = max(matriceId[i][j], matriceId[i-1][j])
							zonaMin = min(matriceId[i][j], matriceId[i-1][j])
							for x in range(self.N):
								for y in range(self.M):
									if matriceId[x][y] == zonaMax:
										matriceId[x][y] = zonaMin
					elif i != 0 and nodCurent.info[i][j] == nodCurent.info[i-1][j]:
						matriceId[i][j] = matriceId[i-1][j]
					else:
						idMax += 1
						matriceId[i][j] = idMax

		return matriceId, idMax

	def eliminaPiesa(self, matriceId, copieMatrice, id):
		"""
				Elimin piesa din starea curenta.

			Args:
				    matriceId (list): O matrice de id-uri ce reprezinta fiecare piesa unica,
				    copieMatrice(list): Copia matricei starii curente.
				    id int(): id-ul piesei ce trebuie eliminata.

		    Returns:
		        culoare

		        """
		culoare = ''
		for i in range(self.N):
			for j in range(self.M):
				if matriceId[i][j] == id:
					culoare = copieMatrice[i][j]
					copieMatrice[i][j] = '#'

		return culoare

	def verificarePiesa(self, copieMatrice):	#de reparat
		"""
				Generez miscarile pieselor pentru a umple spatiile goale.

			Args:
				    copieMatrice(list): Copia matricei starii curente.
				    
		    Returns:
		        True daca o piesa s-a deplasat, False daca nu.

		        """
		flag = 1
		for i in range(self.N):
			for j in range(self.M):
				if i != 0 and copieMatrice[i][j] == '#' and copieMatrice[i - 1][j] != '#':
					flag = 0
					copieMatrice[i][j] = copieMatrice[i - 1][j]
					copieMatrice[i - 1][j] = '#'

		for i in range(self.N):
			for j in range(self.M):
				if (j != self.M - 1) and copieMatrice[i][j] == '#' and copieMatrice[i][j + 1] != '#':
					flag = 0
					copieMatrice[i][j] = copieMatrice[i][j + 1]
					copieMatrice[i][j + 1] = '#'

		return flag

	def genereazaSuccesori(self, nodCurent, tip_euristica="euristica_banala"):
		listaSuccesori = []
		matriceId, idMax = self.umple_matriceId(nodCurent, [[0] * self.M for i in range(self.N)])

		dictFrecventa = self.frecventa(nodCurent)
		for id in range(1, idMax+1):
			copieMatrice = copy.deepcopy(nodCurent.info)
			culoare = self.eliminaPiesa(matriceId, copieMatrice, id)
			if culoare == '':
				continue
			flag = 0
			while flag == 0:
				flag = self.verificarePiesa(copieMatrice)

			dictFrecventaDupaEliminare = self.frecventa(nodCurent)
			cost = ((1 + dictFrecventaDupaEliminare[culoare]) //
					dictFrecventa[culoare])

			nodNou = NodParcurgere(copieMatrice, nodCurent, nodCurent.g + cost,
					self.calculeaza_h(nodCurent.info, matriceId, id, tip_euristica))

			listaSuccesori.append(nodNou)
		return listaSuccesori

	def calculeaza_h(self, infoNod, matriceId, id, tip_euristica="euristica_banala"):
		if tip_euristica == "euristica_banala":
			if infoNod not in self.scopuri:
				return 1
			return 0

		elif tip_euristica == "euristica_admisibila_1":
			dictCulori = {}
			h = 0
			for i in range(self.N):
				for j in range(self.M):
					if infoNod[i][j] != '#':
						if infoNod[i][j] not in dictCulori:
							dictCulori[infoNod[i][j]] = 1
							h += 1
			return h

		elif tip_euristica == "euristica_admisibila_2":
			dictCulori = {}
			h = 0
			distante = []
			for i in range(self.N):
				for j in range(self.M):
					if infoNod[i][j] != '#':
						if infoNod[i][j] not in dictCulori:
							dictCulori[infoNod[i][j]] = 1
							h += 1
						else:
							dictCulori[infoNod[i][j]] += 1

			for key, value in dictCulori.items():
				if value >= self.k:
					return h
				else:
					for idx1A in range(self.N):
						for idx1B in range(self.M):
							if matriceId[idx1A][idx1B] == id:
								idsPieseDeParcurs = []
								for idx2A in range(self.N):
									for idx2B in range(self.M):
										if infoNod[idx1A][idx1B] == infoNod[idx2A][idx2B] \
												and matriceId[idx1A][idx1B] != matriceId[idx2A][idx2B]:
											h = 0
											if idx2A <= idx1A: 							#sus / sus pe aceeasi linie
												if idx2B <= idx1B:						#stanga sus / sus pe aceeasi coloana
													for idx1 in range(idx2A, idx1A+1):
														for idx2 in range(idx2B, idx1B+1):
															if matriceId[idx1][idx2] != matriceId[idx1A][idx1B] and \
																	matriceId[idx1][idx2] != matriceId[idx2A][idx2B] and \
																	(matriceId[idx1][idx2] not in idsPieseDeParcurs):
																		idsPieseDeParcurs.append(matriceId[idx1][idx2])
																		h += 1
												else:							# dreapta sus
													for idx1 in range(idx2A, idx1A):
														for idx2 in range(idx1B, idx2B):
															if matriceId[idx1][idx2] != matriceId[idx1A][idx1B] and \
																	matriceId[idx1][idx2] != matriceId[idx2A][idx2B] and (
																	matriceId[idx1][idx2] not in idsPieseDeParcurs):
																idsPieseDeParcurs.append(matriceId[idx1][idx2])
																h += 1
											else:								#jos
												if idx2B < idx1B:				#stanga jos
													for idx1 in range(idx1A, idx2A+1):
														for idx2 in range(idx2B, idx1B+1):
															if matriceId[idx1][idx2] != matriceId[idx1A][idx1B] and \
																	matriceId[idx1][idx2] != matriceId[idx2A][idx2B] and \
																	(matriceId[idx1][idx2] not in idsPieseDeParcurs):
																idsPieseDeParcurs.append(matriceId[idx1][idx2])
																h += 1
												elif idx2B > idx1B:				#dreapta jos
													for idx1 in range(idx1A, idx2A+1):
														for idx2 in range(idx1B, idx2B+1):
															if matriceId[idx1][idx2] != matriceId[idx1A][idx1B] and \
																	matriceId[idx1][idx2] != matriceId[idx2A][idx2B] and \
																	(matriceId[idx1][idx2] not in idsPieseDeParcurs):
																idsPieseDeParcurs.append(matriceId[idx1][idx2])
																h += 1
											distante.append(h)
					return min(distante)

		elif tip_euristica == "euristica_neadmisibila":
			dictCulori = {}
			h = 0
			for i in range(self.N):
				for j in range(self.M):
					if infoNod[i][j] != '#':
						if infoNod[i][j] not in dictCulori:
							dictCulori[infoNod[i][j]] = 1
							h += 2
			return h

@stopit.threading_timeoutable(default="Intrat in timeout")
def breadth_first(gr, nrSolutiiCautate):
	t1 = time.time()

	if gr.nuAreSolutii() == 0:
		f.write("Nu are solutii!")
		return
	# in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
	c = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, None, None))]

	while len(c) > 0:
		#f.write("Coada actuala: " + str(c) + '\n')
		nodCurent = c.pop(0)

		if gr.testeaza_scop(nodCurent):
			f.write("\nSolutie:")
			nodCurent.afisDrum()
			t2 = time.time()
			f.write("\nTimp de gasire a solutiei: " + str(round(t2-t1, 3)) + " secunde")
			f.write("\n\n-----------------------\n\n")
			nrSolutiiCautate -= 1
			if nrSolutiiCautate == 0:
				return
		lSuccesori = gr.genereazaSuccesori(nodCurent)
		c.extend(lSuccesori)

@stopit.threading_timeoutable(default="Intrat in timeout")
def depth_first(gr, nrSolutiiCautate):
	t1 = time.time()
	if gr.nuAreSolutii() == 0:
		f.write("Nu are solutii!")
		return
	# vom simula o stiva prin relatia de parinte a nodului curent
	df(NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, None, None)), nrSolutiiCautate, t1)
def df(nodCurent, nrSolutiiCautate, t1):
	if nrSolutiiCautate <= 0:  # testul acesta s-ar valida doar daca in apelul initial avem df(start,if nrSolutiiCautate=0)
		return nrSolutiiCautate
	#f.write("Stiva actuala: " + str(nodCurent.obtineDrum()) + '\n')
	if gr.testeaza_scop(nodCurent):
		f.write("Solutie: ")
		nodCurent.afisDrum()
		t2 = time.time()
		f.write("\nTimp de gasire a solutiei: " + str(round(t2 - t1, 3)) + " secunde")
		f.write("\n\n-----------------------\n\n")
		nrSolutiiCautate -= 1
		if nrSolutiiCautate == 0:
			return nrSolutiiCautate
	lSuccesori = gr.genereazaSuccesori(nodCurent)
	for sc in lSuccesori:
		if nrSolutiiCautate != 0:
			nrSolutiiCautate = df(sc, nrSolutiiCautate, t1)

	return nrSolutiiCautate

@stopit.threading_timeoutable(default="Intrat in timeout")
def depth_first_iterativ(gr, nrSolutiiCautate):
	t1 = time.time()
	if gr.nuAreSolutii() == 0:
		f.write("Nu are solutii!")
		return
	for i in range(1, gr.N+1):
		if nrSolutiiCautate == 0:
			return
		#f.write("\n**************\n\nAdancime maxima: " + str(i) + '\n\n')
		nrSolutiiCautate=dfi(NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, None, None)), i, nrSolutiiCautate, t1)
def dfi(nodCurent, adancime, nrSolutiiCautate, t1):
	#f.write("Stiva actuala: " + str(nodCurent.obtineDrum()) + '\n')
	if adancime == 1 and gr.testeaza_scop(nodCurent):
		f.write("Solutie: ")
		nodCurent.afisDrum()
		t2 = time.time()
		f.write("\nTimp de gasire a solutiei: " + str(round(t2 - t1, 3)) + " secunde")
		f.write("\n\n-----------------------\n\n")
		nrSolutiiCautate -= 1
		if nrSolutiiCautate == 0:
			return nrSolutiiCautate
	if adancime > 1:
		lSuccesori=gr.genereazaSuccesori(nodCurent)
		for sc in lSuccesori:
			if nrSolutiiCautate!=0:
				nrSolutiiCautate=dfi(sc, adancime-1, nrSolutiiCautate, t1)
	return nrSolutiiCautate

@stopit.threading_timeoutable(default="Intrat in timeout")
def a_star(gr, nrSolutiiCautate, tip_euristica):
	t1 = time.time()
	# in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
	if gr.nuAreSolutii() == 0:
		f.write("Nu are solutii!")
		return
	c = queue.PriorityQueue()
	c.put(NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, None, None)))

	while not c.empty():
		nodCurent = c.get()
		if gr.testeaza_scop(nodCurent):
			f.write("Solutie: ")
			nodCurent.afisDrum()
			t2 = time.time()
			f.write("\nTimp de gasire a solutiei: " + str(round(t2 - t1, 3)) + " secunde")
			f.write("\n\n-----------------------\n\n")
			nrSolutiiCautate -= 1
			if nrSolutiiCautate == 0:
				return
		lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
		for s in lSuccesori:
			c.put(s)

@stopit.threading_timeoutable(default="Intrat in timeout")
def a_star_optimizat(gr, tip_euristica):
	t1 = time.time()
	if gr.nuAreSolutii() == 0:
		f.write("Nu are solutii!")
		return
	# in coada vom avea doar noduri de tip NodParcurgere (nodurile din arborele de parcurgere)
	l_open = [NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, None, None))]

	# l_open contine nodurile candidate pentru expandare (este echivalentul lui c din A* varianta neoptimizata)

	# l_closed contine nodurile expandate
	l_closed = []
	while len(l_open) > 0:
		#f.write("Coada actuala: " + str(l_open) + '\n')
		nodCurent = l_open.pop(0)
		l_closed.append(nodCurent)
		if gr.testeaza_scop(nodCurent):
			f.write("\nSolutie: ")
			nodCurent.afisDrum()
			t2 = time.time()
			f.write("\nTimp de gasire a solutiei: " + str(round(t2 - t1, 3)) + " secunde")
			f.write("\n\n-----------------------\n\n")
			return
		lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
		for s in lSuccesori:
			gasitC = False
			for nodC in l_open:
				if s.info == nodC.info:
					gasitC = True
					if s.f >= nodC.f:
						lSuccesori.remove(s)
					else:  # s.f<nodC.f
						l_open.remove(nodC)
					break
			if not gasitC:
				for nodC in l_closed:
					if s.info == nodC.info:
						if s.f >= nodC.f:
							lSuccesori.remove(s)
						else:  # s.f<nodC.f
							l_closed.remove(nodC)
						break
		for s in lSuccesori:
			i = 0
			gasit_loc = False
			for i in range(len(l_open)):
				# diferenta fata de UCS e ca ordonez crescator dupa f
				# daca f-urile sunt egale ordonez descrescator dupa g
				if l_open[i].f > s.f or (l_open[i].f == s.f and l_open[i].g <= s.g):
					gasit_loc = True
					break
			if gasit_loc:
				l_open.insert(i, s)
			else:
				l_open.append(s)

@stopit.threading_timeoutable(default="Intrat in timeout")
def ida_star(gr, nrSolutiiCautate, tip_euristica="euristica_banala"):
	t1 = time.time()
	if gr.nuAreSolutii() == 0:
		f.write("Nu are solutii!")
		return

	nodStart = NodParcurgere(gr.start, None, 0, gr.calculeaza_h(gr.start, None, None))
	limita = nodStart.f
	while True:

		#f.write("Limita de pornire: " + str(limita) + '\n')
		nrSolutiiCautate, rez = construieste_drum(gr, nodStart, limita, nrSolutiiCautate, tip_euristica, t1)
		if rez == "gata":
			break
		if rez == float('inf'):
			f.write("Nu mai exista solutii!")
			break
		limita = rez
		#f.write(">>> Limita noua: " + str(limita) + '. ')
def construieste_drum(gr, nodCurent, limita, nrSolutiiCautate, tip_euristica, t1):
	#f.write("A ajuns la: " + str(nodCurent) + '\n')
	if nodCurent.f > limita:
		return nrSolutiiCautate, nodCurent.f
	if gr.testeaza_scop(nodCurent) and nodCurent.f == limita:
		f.write("Solutie: ")
		nodCurent.afisDrum()
		t2 = time.time()
		f.write("\nTimp de gasire a solutiei: " + str(round(t2 - t1, 3)) + " secunde")
		#f.write("\nLimita: " + str(limita))
		f.write("\n\n-----------------------\n\n")
		nrSolutiiCautate -= 1
		if nrSolutiiCautate == 0:
			return 0, "gata"
	lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
	minim = float('inf')
	for s in lSuccesori:
		nrSolutiiCautate, rez = construieste_drum(gr, s, limita, nrSolutiiCautate, tip_euristica, t1)
		if rez == "gata":
			return 0, "gata"
		#f.write("\nCompara " + str(rez) + " cu " + str(minim) + '\n')
		if rez < minim:
			minim = rez
			#f.write("\nNoul minim: " + str(minim) + '\n')
	return nrSolutiiCautate, minim

def verificareTimeout(rez):
	"""
			Stabileste daca sunt in timeout sau nu.

	   Args:
	       rez (None / int): ia valoarea None sau valoarea data de timeout.

	   """

	if (rez is None):
		f.write("\nFunctia nu a intrat in timeout")
	else:
		f.write(str(rez))

def apelare(gr):
	"""
		Apeleaza programul in functie de argumentele date in terminal.

	   Args:
	       gr (Graph): Graful problemei.

	   """

	rez = 0
	if sys.argv[3] == "a_star":
		rez = a_star(gr, nrSolutiiCautate=int(sys.argv[4]), tip_euristica=sys.argv[5], timeout=int(sys.argv[6]))
	elif sys.argv[3] == "a_star_optimizat":
		rez = a_star_optimizat(gr, tip_euristica=sys.argv[5], timeout=int(sys.argv[6]))
	elif sys.argv[3] == "ida_star":
		rez = ida_star(gr, nrSolutiiCautate=int(sys.argv[4]), tip_euristica=sys.argv[5], timeout=int(sys.argv[6]))
	elif sys.argv[3] == "breadth_first":
		rez = breadth_first(gr, nrSolutiiCautate=int(sys.argv[4]), timeout=int(sys.argv[6]))
	elif sys.argv[3] == "depth_first":
		rez = depth_first(gr, nrSolutiiCautate=int(sys.argv[4]), timeout=int(sys.argv[6]))
	elif sys.argv[3] == "depth_first_iterativ":
		rez = depth_first_iterativ(gr, nrSolutiiCautate=int(sys.argv[4]), timeout=int(sys.argv[6]))
	verificareTimeout(rez)
print("\nProgramul si-a inceput executia\n")


for i in range(len(sys.argv)):
	if i == 0:
		print("Argumentul 0 - numele programului: " + sys.argv[0])
	if i == 1:
		print("Argumentul 1 - folderul de intrare: " + sys.argv[1])
	if i == 2:
		print("Argumentul 2 - folderul de iesire: " + sys.argv[2])
	if i == 3:
		print("Argumentul 3 - algoritmul apelat: " + sys.argv[3])
	if i == 4:
		print("Argumentul 4 - numarul de solutii cerut: " + sys.argv[4])
		if sys.argv[3] == "a_star_optimizat" and sys.argv[4] != '1':
			print("\nA_star_optimizat are doar o solutie de cautat! Atunci nrSolutiiCautate=1\n")
	if i == 5:
		print("Argumentul 5 - euristica folosita: " + sys.argv[5])
	if i == 6:
		print("Argumentul 6 - timpul de timeout: " + sys.argv[6] + " secunde")


for numeFisier in os.listdir(sys.argv[1]):
			numeFisierOutput = "output_" + numeFisier
			gr = Graph(sys.argv[1] + '/' + numeFisier)
			f = open(sys.argv[2] + '/' + numeFisierOutput, "w")
			apelare(gr)
			f.write("\nAfisarea a fost incheiata cu succes!")
			f.close()

print("\nProgramul si-a finalizat executia cu succes :) Verificati fisierele de output pentru rezultate\n")