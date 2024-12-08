Imports System 
Imports System.IO
Imports System.Net.Http
Imports Newtonsoft.Json

Module StockDataPipeline
    ' Constants for the stock API (Alpha Vantage as an example)
    Const ApiKey As String = "YOUR_ALPHA_VANTAGE_API_KEY" ' Replace with your API key
    Const ApiUrl As String = "https://www.alphavantage.co/query"

    ' Entry point for the application
    Sub Main()
        ' Read stock symbols from text file
        Dim symbols As List(Of String) = ReadStockSymbolsFromFile("stocks.txt")

        ' Process each stock symbol
        For Each symbol As String In symbols
            Console.WriteLine($"Processing data for: {symbol}")
            Dim stockData = GetStockData(symbol)

            If stockData IsNot Nothing Then
                PerformAnalysis(stockData, symbol)
            Else
                Console.WriteLine($"No data found for {symbol}.")
            End If
        Next

        ' End of the program
        Console.WriteLine("Stock data pipeline has finished processing.")
        Console.ReadLine()
    End Sub

    ' Function to read stock symbols from a file
    Function ReadStockSymbolsFromFile(filePath As String) As List(Of String)
        Dim symbols As New List(Of String)()

        ' Check if file exists
        If File.Exists(filePath) Then
            ' Read each line from the file and add it to the list
            For Each line As String In File.ReadLines(filePath)
                symbols.Add(line.Trim())
            Next
        Else
            Console.WriteLine($"Error: File {filePath} not found.")
        End If

        Return symbols
    End Function

    ' Function to fetch stock data from Alpha Vantage
    Async Function GetStockData(symbol As String) As Task(Of StockData)
        Dim client As New HttpClient()

        ' Build API request URL
        Dim requestUrl = $"{ApiUrl}?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ApiKey}"

        Try
            ' Send the HTTP request and get the response
            Dim response As HttpResponseMessage = Await client.GetAsync(requestUrl)

            ' If the request is successful, parse the response JSON
            If response.IsSuccessStatusCode Then
                Dim jsonResponse As String = Await response.Content.ReadAsStringAsync()
                Dim data = JsonConvert.DeserializeObject(Of AlphaVantageResponse)(jsonResponse)

                ' Return the stock data
                Return New StockData With {
                    .Symbol = symbol,
                    .TimeSeries = data.TimeSeries
                }
            End If
        Catch ex As Exception
            Console.WriteLine($"Error fetching data for {symbol}: {ex.Message}")
        End Try

        Return Nothing
    End Function

    ' Function to perform analysis on the stock data
    Sub PerformAnalysis(stockData As StockData, symbol As String)
        Console.WriteLine($"Performing analysis for {symbol}...")

        ' Example of simple analysis: Calculate average closing price
        Dim totalClose As Double = 0
        Dim count As Integer = 0

        For Each day In stockData.TimeSeries
            totalClose += day.Value.Close
            count += 1
        Next

        Dim averageClose As Double = totalClose / count
        Console.WriteLine($"Average closing price for {symbol}: {averageClose:F2}")

        ' Example: Display the most recent stock price
        Dim latestDay = stockData.TimeSeries.OrderByDescending(Function(d) d.Key).First()
        Console.WriteLine($"Most recent closing price for {symbol} on {latestDay.Key}: {latestDay.Value.Close:F2}")
    End Sub

    ' Stock data model (deserialized from Alpha Vantage response)
    Class StockData
        Public Property Symbol As String
        Public Property TimeSeries As Dictionary(Of String, StockPrice)
    End Class

    ' Stock price data for a specific day
    Class StockPrice
        Public Property Open As Double
        Public Property High As Double
        Public Property Low As Double
        Public Property Close As Double
        Public Property Volume As Integer
    End Class

    ' Response model for Alpha Vantage API
    Class AlphaVantageResponse
        Public Property TimeSeries As Dictionary(Of String, StockPrice)
    End Class
End Module