
Algoritmo MetodoSimplex
	Definir n, m, nc, i, j, iter, colP, filaP Como Entero;
	Definir base Como Entero;
	Definir T, cj, bi, minimo, razon, razonMin, pivote, factor, valor, eps Como Real;
	Definir optimo, noAcotado Como Logico;
	Definir enc Como Cadena;
	Dimension T[10,20];
	Dimension base[10];
	
	eps <- 0.000001;
	
	Escribir "==============================================";
	Escribir "   METODO SIMPLEX - PROTOTIPO 1.0";
	Escribir "   Maximizar Z con restricciones <=";
	Escribir "==============================================";
	

	Repetir
		Escribir "Numero de variables de decision (1 a 8): ";
		Leer n;
	Hasta Que n >= 1 Y n <= 8
	Repetir
		Escribir "Numero de restricciones (1 a 8): ";
		Leer m;
	Hasta Que m >= 1 Y m <= 8
	
	nc <- n + m + 1;   
	Para i <- 1 Hasta m + 1 Hacer
		Para j <- 1 Hasta nc Hacer
			T[i,j] <- 0;
		FinPara
	FinPara
	
	
	Escribir "";
	Escribir "--- FUNCION OBJETIVO (Maximizar) ---";
	Para j <- 1 Hasta n Hacer
		Escribir "Coeficiente c", j, " de x", j, ": ";
		Leer cj;
		T[m+1,j] <- -cj;    
	FinPara
	

	Para i <- 1 Hasta m Hacer
		Escribir "";
		Escribir "--- RESTRICCION ", i, " ---";
		Para j <- 1 Hasta n Hacer
			Escribir "Coeficiente de x", j, ": ";
			Leer T[i,j];
		FinPara
		Repetir
			Escribir "Lado derecho b", i, " (debe ser >= 0): ";
			Leer bi;
			Si bi < 0 Entonces
				Escribir "Valor invalido: este prototipo solo admite b >= 0.";
			FinSi
		Hasta Que bi >= 0
		T[i,nc] <- bi;
		T[i,n+i] <- 1;       
		base[i] <- n + i;    
	FinPara
	
	
	iter <- 0;
	optimo <- Falso;
	noAcotado <- Falso;
	
	Mientras No optimo Y No noAcotado Hacer
		
		
		Escribir "";
		Si iter = 0 Entonces
			Escribir "========== TABLA INICIAL ==========";
		SiNo
			Escribir "========== TABLA - ITERACION ", iter, " ==========";
		FinSi
		Escribir Sin Saltar "  Base |";
		Para j <- 1 Hasta n + m Hacer
			Si j <= n Entonces
				enc <- "x" + ConvertirATexto(j);
			SiNo
				enc <- "s" + ConvertirATexto(j - n);
			FinSi
			Escribir Sin Saltar "  ", enc, "  |";
		FinPara
		Escribir "  Sol";
		Para i <- 1 Hasta m Hacer
			Si base[i] <= n Entonces
				enc <- "x" + ConvertirATexto(base[i]);
			SiNo
				enc <- "s" + ConvertirATexto(base[i] - n);
			FinSi
			Escribir Sin Saltar "  ", enc, "   |";
			Para j <- 1 Hasta nc Hacer
				Escribir Sin Saltar "  ", Redon(T[i,j] * 1000) / 1000, "  |";
			FinPara
			Escribir "";
		FinPara
		Escribir Sin Saltar "   Z   |";
		Para j <- 1 Hasta nc Hacer
			Escribir Sin Saltar "  ", Redon(T[m+1,j] * 1000) / 1000, "  |";
		FinPara
		Escribir "";
		
		
		
		colP <- 0;
		minimo <- 0;
		Para j <- 1 Hasta n + m Hacer
			Si T[m+1,j] < minimo - eps Entonces
				minimo <- T[m+1,j];
				colP <- j;
			FinSi
		FinPara
		
		Si colP = 0 Entonces
			
			optimo <- Verdadero;
		SiNo
			Escribir "Columna pivote: ", colP, "  (valor en Z = ", Redon(minimo * 1000) / 1000, ")";
			
		
			filaP <- 0;
			razonMin <- 0;
			Para i <- 1 Hasta m Hacer
				Si T[i,colP] > eps Entonces     
					razon <- T[i,nc] / T[i,colP];
					Si filaP = 0 O razon < razonMin Entonces
						razonMin <- razon;
						filaP <- i;
					FinSi
				FinSi
			FinPara
			
			Si filaP = 0 Entonces
				
				noAcotado <- Verdadero;
			SiNo
				Escribir "Fila pivote: ", filaP, "  (razon minima = ", Redon(razonMin * 1000) / 1000, ")";
				

				pivote <- T[filaP,colP];
				
				Para j <- 1 Hasta nc Hacer
					T[filaP,j] <- T[filaP,j] / pivote;
				FinPara
				
				Para i <- 1 Hasta m + 1 Hacer
					Si i <> filaP Entonces
						factor <- T[i,colP];
						Para j <- 1 Hasta nc Hacer
							T[i,j] <- T[i,j] - factor * T[filaP,j];
						FinPara
					FinSi
				FinPara
				
				base[filaP] <- colP;
				iter <- iter + 1;
			FinSi
		FinSi
	FinMientras
	

	Escribir "";
	Escribir "==============================================";
	Si noAcotado Entonces
		Escribir "El problema es NO ACOTADO (Z crece indefinidamente).";
	SiNo
		Escribir "SOLUCION OPTIMA ENCONTRADA en ", iter, " iteracion(es)";
		Escribir "Z optimo = ", Redon(T[m+1,nc] * 10000) / 10000;
		Para j <- 1 Hasta n Hacer
			valor <- 0;
			Para i <- 1 Hasta m Hacer
				Si base[i] = j Entonces
					valor <- T[i,nc];
				FinSi
			FinPara
			Escribir "x", j, " = ", Redon(valor * 10000) / 10000;
		FinPara
	FinSi
	Escribir "==============================================";
FinAlgoritmo