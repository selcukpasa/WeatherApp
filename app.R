# Load required packages
library(shiny)
library(leaflet)
library(dplyr)
library(rdrop2)
library(stringr)

# --------------------------------------------------
# Define local file path – update this accordingly
local_path <- '<INSERT_YOUR_LOCAL_PATH_HERE>'  # ← Example: "C:/Users/YourName/Desktop/weather_app/data/"

# Check if the user has updated the path
if (grepl("<INSERT_YOUR_LOCAL_PATH_HERE>", local_path)) {
  stop("Please update 'local_path' with the path to your local directory.")
}
# --------------------------------------------------

# Authenticate with Dropbox using the token file
token <- drop_auth(rdstoken = 'token.rds')

# Download the weather.csv file from Dropbox
drop_download('/Apps/weather_app_selcuk/weather_csv/weather.csv',
              local_path = file.path(local_path, 'weather.csv'),
              overwrite = TRUE)

# Load and process the weather data
city_info <- read.csv(file.path(local_path, "weather.csv"))

# Clean and transform data
city_info <- city_info %>%
  mutate(conditions = factor(ifelse(Main_Weather == "overcast clouds", "Overcast",
                                    ifelse(Weather == "Drizzle", "Rain", 
                                           ifelse(Weather == "Mist", "Rain",
                                                  ifelse(Weather == "Smoke", "Overcast", as.character(Weather))))))) %>%
  mutate(weather_main = str_to_title(Main_Weather))

# Define server logic
server <- function(input, output) {
  output$map <- renderLeaflet({
    
    # Define custom weather icons
    weatherIcons <- iconList(
      Clear = makeIcon(iconUrl = "icons/Clear.png", iconWidth = 20, iconHeight = 20),
      Rain = makeIcon(iconUrl = "icons/Rain.png", iconWidth = 20, iconHeight = 20),
      Haze = makeIcon(iconUrl = "icons/Haze.png", iconWidth = 20, iconHeight = 20),
      Snow = makeIcon(iconUrl = "icons/Snow.png", iconWidth = 20, iconHeight = 20),
      Clouds = makeIcon(iconUrl = "icons/Clouds.png", iconWidth = 20, iconHeight = 20),
      Thunderstorm = makeIcon(iconUrl = "icons/Thunderstorm.png", iconWidth = 20, iconHeight = 20),
      Overcast = makeIcon(iconUrl = "icons/Overcast.png", iconWidth = 20, iconHeight = 20)
    )
    
    # Create leaflet map
    leaflet() %>%
      addProviderTiles(providers$Esri.WorldTerrain) %>%
      setView(lat = 30, lng = 30, zoom = 2) %>%
      setMaxBounds(lng1 = -140, lat1 = -70, lng2 = 155, lat2 = 70) %>%
      addMarkers(data = city_info,
                 lng = ~Longitude, 
                 lat = ~Latitude,
                 icon = ~weatherIcons[city_info$conditions],
                 popup = paste(
                   "<b>", city_info$City, ", ", city_info$Country, "</b><br>",
                   "<b>Updated: </b>", city_info$Date, "<br>",
                   "<b>Population: </b>", city_info$Population, "<br>",
                   "<b>Weather: </b>", city_info$weather_main, "<br>",
                   "<b>Temperature: </b>", city_info$temp, "°C<br>",
                   "<b>Wind Speed: </b>", city_info$Wind_Speed, " km/h"
                 ))
  })
}

# Define UI
ui <- fluidPage(
  class = "outer",
  tags$head(includeCSS("styles.css")),
  leafletOutput(outputId = "map", width = "100%", height = "100%")
)

# Run the app
shinyApp(ui = ui, server = server)
