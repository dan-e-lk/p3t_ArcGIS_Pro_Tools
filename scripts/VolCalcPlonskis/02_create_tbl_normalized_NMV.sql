DROP TABLE IF EXISTS normalized_NMV;
CREATE TABLE normalized_NMV AS 

SELECT 'NMV' as METRIC1, POLYID, 'PW' as Spp, M_Pw as ValHa, M_Pw*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_Pw>0
union
SELECT 'NMV' as METRIC1, POLYID, 'PR' as Spp, M_Pr as ValHa, M_Pr*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_Pr>0
union
SELECT 'NMV' as METRIC1, POLYID, 'PJ' as Spp, M_PJ as ValHa, M_PJ*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_PJ>0
union
SELECT 'NMV' as METRIC1, POLYID, 'SB' as Spp, M_SB as ValHa, M_SB*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_SB>0
union
SELECT 'NMV' as METRIC1, POLYID, 'SW' as Spp, M_SW as ValHa, M_SW*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_SW>0
union
SELECT 'NMV' as METRIC1, POLYID, 'BF' as Spp, M_BF as ValHa, M_BF*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_BF>0
union
SELECT 'NMV' as METRIC1, POLYID, 'CE' as Spp, M_CE as ValHa, M_CE*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_CE>0
union
SELECT 'NMV' as METRIC1, POLYID, 'LA' as Spp, M_LA as ValHa, M_LA*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_LA>0
union
SELECT 'NMV' as METRIC1, POLYID, 'HE' as Spp, M_HE as ValHa, M_HE*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_HE>0
union
SELECT 'NMV' as METRIC1, POLYID, 'OC' as Spp, M_OC as ValHa, M_OC*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_OC>0
union
SELECT 'NMV' as METRIC1, POLYID, 'PO' as Spp, M_PO as ValHa, M_PO*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_PO>0
union
SELECT 'NMV' as METRIC1, POLYID, 'PB' as Spp, M_PB as ValHa, M_PB*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_PB>0
union
SELECT 'NMV' as METRIC1, POLYID, 'BW' as Spp, M_BW as ValHa, M_BW*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_BW>0
union
SELECT 'NMV' as METRIC1, POLYID, 'YB' as Spp, M_YB as ValHa, M_YB*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_YB>0
union
SELECT 'NMV' as METRIC1, POLYID, 'MH' as Spp, M_MH as ValHa, M_MH*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_MH>0
union
SELECT 'NMV' as METRIC1, POLYID, 'MR' as Spp, M_MR as ValHa, M_MR*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_MR>0
union
SELECT 'NMV' as METRIC1, POLYID, 'AX' as Spp, M_AX as ValHa, M_AX*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_AX>0
union
SELECT 'NMV' as METRIC1, POLYID, 'BD' as Spp, M_BD as ValHa, M_BD*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_BD>0
union
SELECT 'NMV' as METRIC1, POLYID, 'BE' as Spp, M_BE as ValHa, M_BE*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_BE>0
union
SELECT 'NMV' as METRIC1, POLYID, 'QR' as Spp, M_QR as ValHa, M_QR*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_QR>0
UNION SELECT 'NMV' as METRIC1, POLYID, 'OH' as Spp, M_OH as ValHa, M_OH*[Ha] as ValTot
from forest_metrics_query where METRIC = 'NMV' and M_OH>0;