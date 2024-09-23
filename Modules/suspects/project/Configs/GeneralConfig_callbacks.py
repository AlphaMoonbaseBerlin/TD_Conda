'''Info Header Start
Name : GeneralConfig_callbacks
Author : Wieland@AMB-ZEPH15
Saveorigin : Project.toe
Saveversion : 2022.35320
Info Header End'''

def GetConfigSchema(configModule:"SchemaObjects", configComp:"JsonConfig") -> dict:
	positiveValue = configModule.ConfigValue(default = 4, validator = lambda value : value > 0)
	
	return {
		"NamedList" : configModule.NamedList(),
    	"Some_Integer" : configModule.ConfigValue( 
			default = -2, 
			validator = lambda value: value < 4,
			typecheck = (float, int)
		 ),
    	"Some_String"   : configModule.ConfigValue( default = "foo", validator= lambda value: isinstance( value, str)),
    	"Subdata" : configModule.CollectionDict({
        	"Sub" : configModule.ConfigValue( default = 13, validator= lambda value: value < 14 ),
			"SubDict" : configModule.CollectionDict({
				"SubSubValue" : configModule.ConfigValue( 
					default = "Foobar",
					typecheck = str,
					parser = lambda value: value.upper()
				)
			})
    		}),
    	"Sublist" : configModule.CollectionList( ),
	    "Prefilled_Sublist" : configModule.CollectionList(
			["Hello", "WOrld"]
		),
		"PositiveValue" : positiveValue(),
		"Prefilled_Validated" : configModule.CollectionList(
			items = [1,2,3],
			default_member = configModule.ConfigValue(default = -1, validator = lambda value: value < 3)
		)
		}
		
		
#def GetConfigData():
#	return a jsonString. Can be used to fetch API data or similiar.
#	return ""