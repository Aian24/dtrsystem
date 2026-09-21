================================================================================
   DTR MANAGEMENT SYSTEM (32-BIT) - WINDOWS 7 PREREQUISITES & INSTALLATION GUIDE
================================================================================

If you are running on Windows 7 SP1 (32-bit), follow these steps in order:

STEP 0: INSTALL ROOT CERTIFICATES (Fixes "certificate chain" error in .NET 4.8)
-----------------------------------------------------------------------------
1. Open the "Windows7_Prerequisites" folder.
2. Right-click "0_Install_Certificates.bat" -> "Run as administrator".
   (Or double-click "MicRooCerAut2011_2011_03_22.crt" -> "Install Certificate" 
    -> Place in "Trusted Root Certification Authorities").

STEP 1: INSTALL UPDATE KB3063858
-----------------------------------------------------------------------------
1. Right-click "Install_KB3063858_DISM.bat" -> "Run as administrator".
2. Wait for it to complete.

STEP 2: INSTALL VISUAL C++ REDISTRIBUTABLE (x86)
-----------------------------------------------------------------------------
1. Right-click "2_vc_redist.x86.exe" -> "Run as administrator".
2. Follow the wizard to complete installation.

STEP 3: INSTALL .NET FRAMEWORK 4.8
-----------------------------------------------------------------------------
1. Right-click "3_ndp48-x86-x64-allos-enu.exe" -> "Run as administrator".
2. Follow the installation wizard to completion.
3. RESTART YOUR COMPUTER when prompted.

STEP 4: RUN DTR MANAGEMENT SYSTEM
-----------------------------------------------------------------------------
- For normal use: Double-click "DTR_Management_System.exe"
- For troubleshooting: Double-click "run_diagnostics.bat"
================================================================================
