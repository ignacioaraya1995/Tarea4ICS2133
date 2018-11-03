import random,sys
import numpy as np

#Se aplican los costos de inventario cuando se revisa
def intWithCommas(number):
    return round(number,2)

def promediarLista(lista):
    sum=0
    for i in lista:
        sum=sum+i
    return sum/len(lista)

def varianzaLista(lista):
    prom = promediarLista(lista)
    sum = 0
    for elem in lista:
        sum += (elem - prom)**2
    return round(sum/(len(lista) - 1),3)

class Evento:
    def __init__(self, tipo, tiempo, variable = 0):
        self.tipo = tipo
        self.tiempo = tiempo
        self.variable = variable

    def __str__(self):
        return "Tipo: " + self.tipo + " - Tiempo: " + str(self.tiempo)

    def __repr__(self):
        return "Tipo: " + self.tipo + " - Tiempo: " + str(self.tiempo)

class Compania:

    def __init__(self, inventarioMax, inventarioMin, inventarioInicial, tasaLlegadaDemanda, horizonte, costoInventarioUnitario, costoDemandaPerdidaUnitaria):
        self.inventarioMax = inventarioMax
        self.inventarioMin = inventarioMin
        self.inventario = inventarioInicial
        self.tasaLlegadaDemanda = tasaLlegadaDemanda
        self.horizonte = horizonte
        self.costoInventarioUnitario = costoInventarioUnitario
        self.costoDemandaPerdidaUnitaria = costoDemandaPerdidaUnitaria
        self.ventasTotales = 0
        self.tiempo = 0
        self.eventos = []
        self.demandaPendiente = 0
        self.vecesRepuesto = 0
        self.comprasTotales = 0
        self.GenerarCostos()

    def __str__(self):
        return "Politica: S:{} - s:{}".format(self.inventarioMax, self.inventarioMin)

    def estadisticas(self):
        self.costosTotales = 0
        for i in self.costosMensualesTotales:
            self.costosTotales += self.costosMensualesTotales[i]
        self.costoPromedio = self.costosTotales / len(self.costosMensualesTotales)

    def elegirEvento(self):
        continuar = True
        self.proxDemanda()
        while continuar:
            self.ordenarEventos()
            next = self.eventos[0]
            if next.tiempo <= self.horizonte:
                self.realizarEvento(next)
            else:
                continuar = False

    def realizarEvento(self, next):
        self.eventos.remove(next)
        pasado = self.tiempo
        self.tiempo = next.tiempo
        if next.tipo == "proxDemanda":
            self.calcularCostos(pasado)
            self.compra()
            self.proxDemanda()
        elif next.tipo == "revisarInventario":
            self.calcularCostos(pasado)
            self.pedirInventario()
            self.gastosMensuales()
            self.estadoSistema()
        elif next.tipo == "llegadaInventario":
            self.calcularCostos(pasado)
            self.sumarInventario(next.variable)

    def gastosMensuales(self):
        mesActual = self.tiempo
        self.costosMensualesTotales[mesActual-1] = self.CostosInventarioMensuales[mesActual-1] + self.CostosDemandaPerMensuales[mesActual-1] + self.CostosRepoMensuales[mesActual-1]

    def estadoSistema(self):
        mostrar = False
        if mostrar:
            print("Mes {}".format(self.tiempo))
            print("Inventario({},{}): {}".format(self.inventarioMin, self.inventarioMax,self.inventario))
            print("Unidades Pedidas: {}".format(self.UnidadesPedidasMensuales[self.tiempo-1]))
            print("Unidades Vendidas: {}".format(self.ComprasMensuales[self.tiempo-1]))
            print("Demanda Pendiente: {}".format(self.demandaPendiente))
            print("Costos x Inventario: $ {}".format(round(self.CostosInventarioMensuales[self.tiempo-1],2)))
            print("Costos x DemandaPer: $ {}".format(round(self.CostosDemandaPerMensuales[self.tiempo-1],2)))
            print("Costos x Reposicion: $ {}".format(round(self.CostosRepoMensuales[self.tiempo-1],2)))
            print("Total Gasto del mes: $ {}".format(round(self.costosMensualesTotales[self.tiempo-1],2)))
            print("********************")

    def ordenarEventos(self):
        self.eventos = sorted(self.eventos, key=lambda obj: obj.tiempo)

    def proxDemanda(self):
        demanda = round(np.random.exponential(self.tasaLlegadaDemanda),4)
        tiempo = round(self.tiempo + demanda,4)
        self.eventos.append(Evento("proxDemanda",tiempo))

    def compra(self):
        compras = self.calcularDemanda()
        x = int(self.tiempo)
        if self.inventario > compras:
            self.inventario -= compras
            self.comprasTotales += compras
            self.ComprasMensuales[x] += compras
        elif self.inventario == compras:
            self.inventario = 0
            self.comprasTotales += compras
            self.ComprasMensuales[x] += compras
        elif self.inventario < compras:
            demandaPerdida = compras - self.inventario
            self.comprasTotales += self.inventario
            self.ComprasMensuales[x] += self.inventario
            self.inventario = 0
            self.demandaPendiente += demandaPerdida

    def proxReposiciones(self):
        for i in range (1, self.horizonte + 1):
            self.eventos.append(Evento("revisarInventario",i))

    def pedirInventario(self):
        if self.inventario <= self.inventarioMin:
                pedido = self.inventarioMax - self.inventario
                #print("Pedi {} unidades para el Inventario".format(pedido))
                costo = 32 + 3*pedido
                x = int(self.tiempo)
                self.CostosRepoMensuales[x-1] += costo
                self.UnidadesPedidasMensuales[x-1] += pedido
                tiempo = round(self.tiempo + random.uniform(0.5,1),4)
                self.eventos.append(Evento("llegadaInventario", tiempo, pedido))

    def sumarInventario(self, pedido):
        self.vecesRepuesto +=1
        self.inventario += pedido
        if self.demandaPendiente == 0:
            pass
        elif 0 < self.demandaPendiente < self.inventario:
            self.inventario -= self.demandaPendiente
            self.comprasTotales += self.demandaPendiente
            self.ComprasMensuales[int(self.tiempo)] += self.demandaPendiente
            self.demandaPendiente = 0
        elif self.demandaPendiente >= self.inventario:
            self.demandaPendiente -= self.inventario
            self.ComprasMensuales[int(self.tiempo)] += self.inventario
            self.inventario = 0

    def calcularCostos(self, tiempo1):
        tiempo = round(self.tiempo- tiempo1,4)
        y = int(self.tiempo)
        self.CostosInventarioMensuales[y] += 1*self.inventario*tiempo
        self.CostosDemandaPerMensuales[y] += 5*self.demandaPendiente*tiempo


    def calcularDemanda(self):
        prob = round(random.uniform(0,1),4)
        if prob <= 0.3333:
            return 1
        elif 0.3333 < prob <= 0.5:
            return 2
        elif 0.5 < prob <= 0.8333:
            return 3
        else:
            return 4

    def GenerarCostos(self):
        self.costosMensualesTotales = dict()
        self.CostosRepoMensuales = dict()
        self.ComprasMensuales = dict()
        self.UnidadesPedidasMensuales = dict()
        self.CostosInventarioMensuales = dict()
        self.CostosDemandaPerMensuales = dict()
        for i in range(0,self.horizonte + 1):
            self.CostosRepoMensuales[i] = 0
            self.ComprasMensuales[i] = 0
            self.UnidadesPedidasMensuales[i] = 0
            self.CostosInventarioMensuales[i] = 0
            self.CostosDemandaPerMensuales[i] = 0

class ResultadoEscenario:
    def __init__(self, InvMax, InvMin, costos, costoMensual):
        self.InvMax = InvMax
        self.InvMin = InvMin
        self.costos = costos
        self.costoMensual = costoMensual

    def __str__(self):
        return "Escenario ({},{}) - Costo: $ {} - $ Costo Promedio: $ {}".format(self.InvMin,
                self.InvMax, intWithCommas(self.costos), intWithCommas(self.costoMensual))

    def __repr__(self):
        return "Escenario ({},{}) - Costo: $ {}".format(self.InvMin,
                self.InvMax, self.costos)

class Reporte:
    def __init__(self, escenario):
        self.escenario = ""
        self.replicas = dict()

if __name__ == "__main__":
    ################################# datos ####################################
    inventarioInicial = 60
    tasaLlegadaDemanda = 0.1
    horizonte = 120 #meses
    costoInventarioUnitario = 1
    costoDemandaPerdidaUnitaria = 5
    #politicas= [(20,40)]
    politicas = [(20,40),(20,50),(20,60),(20,70),(20,80),(25,60),(25,70)]
    #politicas = [(20,40),(20,80),(40,60),(40,100),(60,100)]
    #politicas = [(20,40),(20,60),(25,60),(0,100),(100,200),(0,10),(50,100)]
    replicas = 660
    escribirDocumento = True
    stop = False
    SEED = 419951
    ############################################################################
    file = open('/Users/ignacioaraya/Desktop/to-do/Tarea 4 ICS2123/preg2k.csv','w')
    file2 = open('/Users/ignacioaraya/Desktop/to-do/Tarea 4 ICS2123/preg22k.csv','w')
    resultados = []
    reportes = []
    ############################################################################

    print("* * * * * * * * * Datos * * * * * * * * * *")
    print("* Replicas por Escenario: {}              *".format(replicas))
    print("* Horizonte de cada Escenario: {} meses  *".format(horizonte))
    print("* Inventario Inicial: {} unidades         *".format(inventarioInicial))
    print("* Costo Inventario: $ {} por unidad        *".format(costoInventarioUnitario))
    print("* Costo Demanda Perdida: $ {} por unidad   *".format(costoDemandaPerdidaUnitaria))
    print("* Tasa llegada de demandas: ~ Exp({})    *".format(tasaLlegadaDemanda))
    print("* * * * * * * * * * * * * * * * * * * * * *")
    for politica in politicas:
        inventarioMin = politica[0]
        inventarioMax = politica[1]
        escenario = "({};{})".format(inventarioMin, inventarioMax)
        print("Escenario: {}".format(escenario))
        reporte = Reporte(escenario)
        reporte.escenario = escenario
        costoPromedioTotal = []
        costoPromedioMensual = []
        for i in range(0,replicas+1):
            np.random.seed(SEED + i)
            c = Compania(inventarioMax, inventarioMin, inventarioInicial,
            tasaLlegadaDemanda, horizonte, costoInventarioUnitario, costoDemandaPerdidaUnitaria)
            c.proxReposiciones()
            c.elegirEvento()
            c.estadisticas()
            costoPromedioTotal.append(c.costosTotales)
            costoPromedioMensual.append(c.costoPromedio + 3)
            reporte.replicas[i] = round(c.costoPromedio,2)
            i +=1

        costoPromedioTotal = sum(costoPromedioTotal) / len(costoPromedioTotal)
        costoPromedioMensual = sum(costoPromedioMensual) / len(costoPromedioMensual)
        reporte.replicas["promedio"] = round(costoPromedioMensual,2)
        resultados.append(ResultadoEscenario(inventarioMax, inventarioMin, costoPromedioTotal, costoPromedioMensual))
        reportes.append(reporte)
    #resultados = sorted(resultados, key=lambda obj: obj.costos)
    for r in resultados:
        print(r)
    if escribirDocumento:
        file.write("replica j,X1j = {},X2j = {},X3j = {},X4j = {},X5j = {},X6j = {},X7j = {}\n".format(reportes[0].escenario,reportes[1].escenario,reportes[2].escenario,reportes[3].escenario,reportes[4].escenario,reportes[5].escenario,reportes[6].escenario))
        for i in range(replicas):
            file.write("{},{},{},{},{},{},{},{}\n".format(i+1,reportes[0].replicas[i+1], reportes[1].replicas[i+1], reportes[2].replicas[i+1], reportes[3].replicas[i+1], reportes[4].replicas[i+1], reportes[5].replicas[i+1], reportes[6].replicas[i+1]))
        file.write("Promedio,{},{},{},{},{},{},{}".format(reportes[0].replicas["promedio"], reportes[1].replicas["promedio"], reportes[2].replicas["promedio"], reportes[3].replicas["promedio"], reportes[4].replicas["promedio"], reportes[5].replicas["promedio"], reportes[6].replicas["promedio"]))
        file.close()
        if stop:
            sys.exit()
        ################################################################################

        file2.write("replica j,Zj = X1 - X2, Zj = X1 - X3, Zj = X1 - X4, Zj = X1 - X5, Zj = X1 - X6, Zj = X1 - X7, Zj = X2 - X3, Zj = X2 - X4, Zj = X2 - X5, Zj = X2 - X6, Zj = X2 - X7, Zj = X3 - X4,  Zj = X3 - X5, Zj = X3 - X6, Zj = X3 - X7, Zj = X4 - X5, Zj = X4 - X6, Zj = X5 - X7, Zj = X5 - X6, Zj = X5 - X7, Zj = X6 - X7")
        Lz01 = list()
        Lz02 = list()
        Lz03 = list()
        Lz04 = list()
        Lz05 = list()
        Lz06 = list()
        Lz12 = list()
        Lz13 = list()
        Lz14 = list()
        Lz15 = list()
        Lz16 = list()
        Lz23 = list()
        Lz24 = list()
        Lz25 = list()
        Lz26 = list()
        Lz34 = list()
        Lz35 = list()
        Lz36 = list()
        Lz45 = list()
        Lz46 = list()
        Lz56 = list()
        for i in range(-1,replicas):
            z01 = reportes[0].replicas[i+1] - reportes[1].replicas[i+1]
            z02 = reportes[0].replicas[i+1] - reportes[2].replicas[i+1]
            z03 = reportes[0].replicas[i+1] - reportes[3].replicas[i+1]
            z04 = reportes[0].replicas[i+1] - reportes[4].replicas[i+1]
            z05 = reportes[0].replicas[i+1] - reportes[5].replicas[i+1]
            z06 = reportes[0].replicas[i+1] - reportes[6].replicas[i+1]
            Lz01.append(z01)
            Lz02.append(z02)
            Lz03.append(z03)
            Lz04.append(z04)
            Lz05.append(z05)
            Lz06.append(z06)

            z12 = reportes[1].replicas[i+1] - reportes[2].replicas[i+1]
            z13 = reportes[1].replicas[i+1] - reportes[3].replicas[i+1]
            z14 = reportes[1].replicas[i+1] - reportes[4].replicas[i+1]
            z15 = reportes[1].replicas[i+1] - reportes[5].replicas[i+1]
            z16 = reportes[1].replicas[i+1] - reportes[6].replicas[i+1]
            Lz12.append(z12)
            Lz13.append(z13)
            Lz14.append(z14)
            Lz15.append(z15)
            Lz16.append(z16)

            z23 = reportes[2].replicas[i+1] - reportes[3].replicas[i+1]
            z24 = reportes[2].replicas[i+1] - reportes[4].replicas[i+1]
            z25 = reportes[2].replicas[i+1] - reportes[5].replicas[i+1]
            z26 = reportes[2].replicas[i+1] - reportes[6].replicas[i+1]
            Lz23.append(z23)
            Lz24.append(z24)
            Lz25.append(z25)
            Lz26.append(z26)


            z34 = reportes[3].replicas[i+1] - reportes[4].replicas[i+1]
            z35 = reportes[3].replicas[i+1] - reportes[5].replicas[i+1]
            z36 = reportes[3].replicas[i+1] - reportes[6].replicas[i+1]
            Lz34.append(z34)
            Lz35.append(z35)
            Lz36.append(z36)


            z45 = reportes[4].replicas[i+1] - reportes[5].replicas[i+1]
            z46 = reportes[4].replicas[i+1] - reportes[6].replicas[i+1]
            Lz45.append(z45)
            Lz46.append(z46)


            z56 = reportes[5].replicas[i+1] - reportes[6].replicas[i+1]
            Lz56.append(z56)
            file2.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(i,z01,z02,z03,z04,z05,z06, z12,z13,z14,z15,z16, z23, z24, z25, z26, z34,z35,z36, z45,z46,z56))
        file2.write("Promedio,{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(promediarLista(Lz01),promediarLista(Lz02),promediarLista(Lz03),promediarLista(Lz04),promediarLista(Lz05),promediarLista(Lz06),promediarLista(Lz12),promediarLista(Lz13),promediarLista(Lz14),promediarLista(Lz15),promediarLista(Lz16),promediarLista(Lz23), promediarLista(Lz24), promediarLista(Lz25),promediarLista(Lz26),promediarLista(Lz34),promediarLista(Lz35),promediarLista(Lz36),promediarLista(Lz45),promediarLista(Lz46),promediarLista(Lz56)))
        HA = True

        if HA:
            file2.write("Varianza,{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(varianzaLista(Lz01),varianzaLista(Lz02),varianzaLista(Lz03),varianzaLista(Lz04),varianzaLista(Lz05),varianzaLista(Lz06),varianzaLista(Lz12),varianzaLista(Lz13),varianzaLista(Lz14),varianzaLista(Lz15),varianzaLista(Lz16),varianzaLista(Lz23), varianzaLista(Lz24), varianzaLista(Lz25),varianzaLista(Lz26),varianzaLista(Lz34),varianzaLista(Lz35),varianzaLista(Lz36),varianzaLista(Lz45),varianzaLista(Lz46),varianzaLista(Lz56)))
            t = 1.96

            AnchoZ01 = round(t*(varianzaLista(Lz01)**.5),2)
            AnchoZ02 = round(t*(varianzaLista(Lz02)**.5),2)
            AnchoZ03 = round(t*(varianzaLista(Lz03)**.5),2)
            AnchoZ04 = round(t*(varianzaLista(Lz04)**.5),2)
            AnchoZ05 = round(t*(varianzaLista(Lz05)**.5),2)
            AnchoZ06 = round(t*(varianzaLista(Lz06)**.5),2)
            AnchoZ12 = round(t*(varianzaLista(Lz12)**.5),2)
            AnchoZ13 = round(t*(varianzaLista(Lz13)**.5),2)
            AnchoZ14 = round(t*(varianzaLista(Lz14)**.5),2)
            AnchoZ15 = round(t*(varianzaLista(Lz15)**.5),2)
            AnchoZ16 = round(t*(varianzaLista(Lz16)**.5),2)
            AnchoZ23 = round(t*(varianzaLista(Lz23)**.5),2)
            AnchoZ24 = round(t*(varianzaLista(Lz24)**.5),2)
            AnchoZ25 = round(t*(varianzaLista(Lz25)**.5),2)
            AnchoZ26 = round(t*(varianzaLista(Lz26)**.5),2)
            AnchoZ34 = round(t*(varianzaLista(Lz34)**.5),2)
            AnchoZ35 = round(t*(varianzaLista(Lz35)**.5),2)
            AnchoZ36 = round(t*(varianzaLista(Lz36)**.5),2)
            AnchoZ45 = round(t*(varianzaLista(Lz45)**.5),2)
            AnchoZ46 = round(t*(varianzaLista(Lz46)**.5),2)
            AnchoZ56 = round(t*(varianzaLista(Lz56)**.5),2)

            I01 = "({} ; {})".format(round(promediarLista(Lz01) - AnchoZ01,2), round(promediarLista(Lz01) + AnchoZ01,2))
            I02 = "({} ; {})".format(round(promediarLista(Lz02) - AnchoZ02,2), round(promediarLista(Lz02) + AnchoZ02,2))
            I03 = "({} ; {})".format(round(promediarLista(Lz03) - AnchoZ03,2), round(promediarLista(Lz03) + AnchoZ03,2))
            I04 = "({} ; {})".format(round(promediarLista(Lz04) - AnchoZ04,2), round(promediarLista(Lz04) + AnchoZ04,2))
            I05 = "({} ; {})".format(round(promediarLista(Lz05) - AnchoZ05,2), round(promediarLista(Lz05) + AnchoZ05,2))
            I06 = "({} ; {})".format(round(promediarLista(Lz06) - AnchoZ06,2), round(promediarLista(Lz06) + AnchoZ06,2))
            I12 = "({} ; {})".format(round(promediarLista(Lz12) - AnchoZ12,2), round(promediarLista(Lz12) + AnchoZ12,2))
            I13 = "({} ; {})".format(round(promediarLista(Lz13) - AnchoZ13,2), round(promediarLista(Lz13) + AnchoZ13,2))
            I14 = "({} ; {})".format(round(promediarLista(Lz14) - AnchoZ14,2), round(promediarLista(Lz14) + AnchoZ14,2))
            I15 = "({} ; {})".format(round(promediarLista(Lz15) - AnchoZ15,2), round(promediarLista(Lz15) + AnchoZ15,2))
            I16 = "({} ; {})".format(round(promediarLista(Lz16) - AnchoZ16,2), round(promediarLista(Lz16) + AnchoZ16,2))
            I23 = "({} ; {})".format(round(promediarLista(Lz23) - AnchoZ23,2), round(promediarLista(Lz23) + AnchoZ23,2))
            I24 = "({} ; {})".format(round(promediarLista(Lz24) - AnchoZ24,2), round(promediarLista(Lz24) + AnchoZ24,2))
            I25 = "({} ; {})".format(round(promediarLista(Lz25) - AnchoZ25,2), round(promediarLista(Lz25) + AnchoZ25,2))
            I26 = "({} ; {})".format(round(promediarLista(Lz26) - AnchoZ26,2), round(promediarLista(Lz26) + AnchoZ26,2))
            I34 = "({} ; {})".format(round(promediarLista(Lz34) - AnchoZ34,2), round(promediarLista(Lz34) + AnchoZ34,2))
            I35 = "({} ; {})".format(round(promediarLista(Lz35) - AnchoZ35,2), round(promediarLista(Lz35) + AnchoZ35,2))
            I36 = "({} ; {})".format(round(promediarLista(Lz36) - AnchoZ36,2), round(promediarLista(Lz36) + AnchoZ36,2))
            I45 = "({} ; {})".format(round(promediarLista(Lz45) - AnchoZ45,2), round(promediarLista(Lz45) + AnchoZ45,2))
            I46 = "({} ; {})".format(round(promediarLista(Lz46) - AnchoZ46,2), round(promediarLista(Lz46) + AnchoZ46,2))
            I56 = "({} ; {})".format(round(promediarLista(Lz56) - AnchoZ56,2), round(promediarLista(Lz56) + AnchoZ56,2))


            file2.write("Ancho,{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(AnchoZ01, AnchoZ02, AnchoZ03, AnchoZ04, AnchoZ05, AnchoZ06, AnchoZ12, AnchoZ13, AnchoZ14, AnchoZ15, AnchoZ16, AnchoZ23, AnchoZ24, AnchoZ25, AnchoZ26, AnchoZ34, AnchoZ35, AnchoZ36, AnchoZ45, AnchoZ46, AnchoZ56))

            file2.write("Intervalo,{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(I01,
            I02, I03, I04, I05, I06, I12, I13, I14, I15, I16, I23, I24, I25, I26, I34, I35, I36, I45, I46, I56))

            RZ01 = "NO"
            RZ02 = "NO"
            RZ03 = "NO"
            RZ04 = "NO"
            RZ05 = "NO"
            RZ06 = "NO"
            RZ12 = "NO"
            RZ13 = "NO"
            RZ13 = "NO"
            RZ14 = "NO"
            RZ15 = "NO"
            RZ16 = "NO"
            RZ23 = "NO"
            RZ24 = "NO"
            RZ25 = "NO"
            RZ26 = "NO"
            RZ34 = "NO"
            RZ35 = "NO"
            RZ36 = "NO"
            RZ45 = "NO"
            RZ46 = "NO"
            RZ56 = "NO"

            if AnchoZ01 >= promediarLista(Lz01):
                RZ01 = "SI"
            if AnchoZ02 >= promediarLista(Lz02):
                RZ02 = "SI"
            if AnchoZ03 >= promediarLista(Lz03):
                RZ03 = "SI"
            if AnchoZ04 >= promediarLista(Lz04):
                RZ04 = "SI"
            if AnchoZ05 >= promediarLista(Lz05):
                RZ05 = "SI"
            if AnchoZ06 >= promediarLista(Lz06):
                RZ06 = "SI"
            if AnchoZ12 >= promediarLista(Lz12):
                RZ12 = "SI"
            if AnchoZ13 >= promediarLista(Lz13):
                RZ13 = "SI"
            if AnchoZ14 >= promediarLista(Lz14):
                RZ14 = "SI"
            if AnchoZ15 >= promediarLista(Lz15):
                RZ15 = "SI"
            if AnchoZ16 >= promediarLista(Lz16):
                RZ16 = "SI"
            if AnchoZ23 >= promediarLista(Lz23):
                RZ23 = "SI"
            if AnchoZ24 >= promediarLista(Lz24):
                RZ24 = "SI"
            if AnchoZ25 >= promediarLista(Lz25):
                RZ25 = "SI"
            if AnchoZ26 >= promediarLista(Lz26):
                RZ26 = "SI"
            if AnchoZ34 >= promediarLista(Lz34):
                RZ34 = "SI"
            if AnchoZ35 >= promediarLista(Lz35):
                RZ35 = "SI"
            if AnchoZ36 >= promediarLista(Lz36):
                RZ36 = "SI"
            if AnchoZ45 >= promediarLista(Lz45):
                RZ45 = "SI"
            if AnchoZ46 >= promediarLista(Lz46):
                RZ46 = "SI"
            if AnchoZ56 >= promediarLista(Lz56):
                RZ56 = "SI"

            file2.write("Intervalo,{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(RZ01,RZ02, RZ03, RZ04, RZ05, RZ06, RZ12, RZ13, RZ14, RZ15, RZ16, RZ23, RZ24, RZ25, RZ26, RZ34, RZ35, RZ36, RZ45, RZ46, RZ56))



        file2.close()
