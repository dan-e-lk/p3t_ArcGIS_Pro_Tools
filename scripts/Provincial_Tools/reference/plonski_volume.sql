SELECT 
tbl_plonski_metrics.METRIC, forest.POLYID, forest.HA, forest.HT, forest.STKG, forest.SC, tbl_ac.AC_5, forest.PLANFU, forest.PFT, 
([tbl_plonski_metrics].[Pw]*([forest].[Pw]/100)*[STKG]) AS M_Pw, ([tbl_plonski_metrics].[PR]*([forest].[PR]/100)*[STKG]) AS M_PR, 
([tbl_plonski_metrics].[PJ]*([forest].[PJ]/100)*[STKG]) AS M_PJ, ([tbl_plonski_metrics].[SB]*([forest].[SB]/100)*[STKG]) AS M_SB, 
([tbl_plonski_metrics].[SW]*([forest].[SW]/100)*[STKG]) AS M_SW, ([tbl_plonski_metrics].[BF]*([forest].[BF]/100)*[STKG]) AS M_BF, 
([tbl_plonski_metrics].[CE]*([forest].[CE]/100)*[STKG]) AS M_CE, ([tbl_plonski_metrics].[LA]*([forest].[LA]/100)*[STKG]) AS M_LA, 
([tbl_plonski_metrics].[HE]*([forest].[HE]/100)*[STKG]) AS M_HE, ([tbl_plonski_metrics].[CE]*([forest].[OC]/100)*[STKG]) AS M_OC, 
([tbl_plonski_metrics].[PO]*([forest].[PO]/100)*[STKG]) AS M_PO, ([tbl_plonski_metrics].[PO]*([forest].[PB]/100)*[STKG]) AS M_PB, 
([tbl_plonski_metrics].[BW]*([forest].[BW]/100)*[STKG]) AS M_BW, ([tbl_plonski_metrics].[OH]*([forest].[YB]/100)*[STKG]) AS M_YB, 
([tbl_plonski_metrics].[MH]*([forest].[MH]/100)*[STKG]) AS M_MH, ([tbl_plonski_metrics].[OH]*([forest].[MR]/100)*[STKG]) AS M_MR, 
([tbl_plonski_metrics].[OH]*(([AB]+[AW])/100)*[STKG]) AS M_AX, ([tbl_plonski_metrics].[OH]*([forest].[BD]/100)*[STKG]) AS M_BD, 
([tbl_plonski_metrics].[OH]*([forest].[BE]/100)*[STKG]) AS M_BE, ([tbl_plonski_metrics].[OH]*(([QR]+[OB]+[OW])/100)*[STKG]) AS M_QR, 

([tbl_plonski_metrics].[OH]*(([forest].[OH]+[CH]+[EX]+[IW])/100)*[STKG]) AS M_OH

FROM (forest INNER JOIN tbl_ac ON forest.AGE = tbl_ac.AGE) 

INNER JOIN tbl_plonski_metrics ON (forest.SC = tbl_plonski_metrics.SC) AND (tbl_ac.AC_5 = tbl_plonski_metrics.AC_5)

WHERE (((tbl_plonski_metrics.METRIC)='GTV') AND ((forest.POLYTYPE)='FOR'));