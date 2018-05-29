echo Loading data

		call stardog namespace add --prefix owl  			--uri http://www.w3.org/2002/07/owl#					risis
		call stardog namespace add --prefix void  			--uri http://rdfs.org/ns/void#							risis
		call stardog namespace add --prefix bdb  			--uri http://vocabularies.bridgedb.org/ops#				risis
		call stardog namespace add --prefix prov  			--uri http://www.w3.org/ns/prov#						risis
		call stardog namespace add --prefix skos  			--uri http://www.w3.org/2004/02/skos/core#				risis
		call stardog namespace add --prefix lens 			--uri http://risis.eu/lens/ 							risis
		call stardog namespace add --prefix risis 			--uri http://risis.eu/ risis							risis
		call stardog namespace add --prefix riclass 		--uri http://risis.eu/class/ 							risis
		call stardog namespace add --prefix schema 			--uri http://risis.eu/ontology/ 						risis
		call stardog namespace add --prefix dataset 		--uri http://risis.eu/dataset/ 							risis
		call stardog namespace add --prefix idea 			--uri http://risis.eu/activity/ 						risis
		call stardog namespace add --prefix linkset 		--uri http://risis.eu/linkset/ 							risis
		call stardog namespace add --prefix method 			--uri http://risis.eu/method/ 							risis
		call stardog namespace add --prefix ll 				--uri http://risis.eu/alignment/predicate/ 				risis
		call stardog namespace add --prefix tmpgraph 		--uri http://risis.eu/alignment/temp-match/ 			risis
		call stardog namespace add --prefix tempG	 		--uri http://risis.eu/alignment/temp-match/ 			risis
		call stardog namespace add --prefix tmpvocab 		--uri http://risis.eu//temp-match/temp-match/predicate/ risis
		call stardog namespace add --prefix mechanism 		--uri http://risis.eu/mechanism/ 						risis
		call stardog namespace add --prefix singletons 		--uri http://risis.eu/singletons/ 						risis
		call stardog namespace add --prefix justification 	--uri http://risis.eu/justification/ 					risis
		call stardog namespace add --prefix lensOp 			--uri http://risis.eu/lens/operator/ 					risis
		call stardog namespace add --prefix lensOpu 		--uri http://risis.eu/lens/operator/union 				risis
		call stardog namespace add --prefix lensOpi 		--uri http://risis.eu/lens/operator/intersection 		risis
		call stardog namespace add --prefix lensOpt 		--uri http://risis.eu/lens/operator/transitive 			risis
		call stardog namespace add --prefix lensOpd 		--uri http://risis.eu/lens/operator/difference 			risis		
		call stardog namespace add --prefix singletons 		--uri http://risis.eu/singletons/ 						risis
		call stardog namespace add --prefix dataset 		--uri http://risis.eu/dataset/ 							risis
		call stardog namespace add --prefix gadm            --uri http://geo.risis.eu/vocabulary/gadm/              risis
        