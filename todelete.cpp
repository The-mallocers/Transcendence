#include <cstdlib>
#include <iostream>
#include <cmath>
#include "class.cpp"

using namespace std;

//Nouvelles variables
double dt = 1e3;
etoile e1, e2;
double r, fx, fy;


//Creation du menu:
void menu()
{
    int choix=0;
    do{
        cout<<"Que desirez-vous faire ?"<<endl;
        cout<<"Saisissez le numero correspondant a votre choix"<<endl;
        cout<<"1.Changer la masse d'une etoile "<<endl;
        cout<<"2.Changer la masse des deux etoiles "<<endl;
        cout<<"3.Changer la position d'une etoile"<<endl;
        cout<<"4.Changer la position des deux etoiles"<<endl;
        cout<<"5.Changer la masse et la position d'une etoile"<<endl;
        cout<<"6.Changer la masse et la position des deux etoiles"<<endl;
        cout<<"7.Quitter"<<endl;

    cin>>choix;

    if (choix != 1 && choix != 2 && choix !=3 && choix !=4 && choix !=5 && choix !=6 && choix !=7)
    {
        cout<<"choix invalide, veuillez ressaisir un numéro"<<endl;
        return menu();
    }
    if(choix ==1)
    {   
        int choix=0;
        do {
            cout<<"Quelle etoile desirez vous modifier ? Saisissez le numero correspondant a l'etoile:"<<endl;
            cout<<"1."<<e1.getnom()<<endl;
            cout<<"2."<<e2.getnom()<<endl;
            cin>>choix;
        } while( choix <=2);
        
    if (choix == 1 )
    {
        e1.set_mass();
    }
   if (choix == 2 )
    {
        e2.set_mass();
    }
    }

    if(choix==2)
    {
        
        e1.set_mass();

        e2.set_mass();
           
    }
    
    if (choix==3)
    {
            int choix=0;
        do {
            cout<<"Quelle etoile desirez vous modifier ? Saisissez le numero correspondant a l'etoile:"<<endl;
            cout<<"1."<<e1.getnom()<<endl;
            cout<<"2."<<e2.getnom()<<endl;
             cin>>choix;
        } while (choix <=2);
       
    if (choix == 1 )
    {
    
        e1.set_x();
        e1.set_y();
    }
    if (choix == 2 )
    {
        
        e2.set_x();
        e2.set_y();
    }
}
if (choix==4)
    {
        
        e1.set_x();
        e1.set_y();
        e2.set_x();
        e2.set_y();
    }
   if (choix==5)
   {
        int choix=0;
        do {
            cout<<"Quelle etoile desirez vous modifier ? Saisissez le numero correspondant a l etoile:"<<endl;
            cout<<"1."<<e1.getnom()<<endl;
            cout<<"2."<<e2.getnom()<<endl;
            cin>>choix;
        } while(choix<=2);
        
    if (choix == 1 )
    {
        
        e1.set_mass();
        e1.set_x();
        e1.set_y();
    }
    if (choix == 2 )
    {
        
        e2.set_mass();
        e2.set_x();
        e2.set_y();
    }
        
   }
   if (choix==6)
   {
    
        e1.set_mass();
        e1.set_x();
        e1.set_y();
        e2.set_mass();
        e2.set_x();
        e2.set_y();
   }
    if(choix ==7)
    {
        exit(0);
    }
    
 } while(choix <= 6);

        for (int i = 0; i < 10000; ++i) {
            // Calculer la distance entre les deux étoiles
            r = sqrt(pow(e2.getx() - e1.getx(), 2) + pow(e2.gety() - e1.gety(), 2));
    
            // Calcul de la force gravitationnelle
            fx = G * e1.getmass() * e2.getmass() * (e2.getx() - e1.getx()) / pow(r, 3);
            fy = G * e1.getmass() * e2.getmass() * (e2.gety() - e1.gety()) / pow(r, 3);
    
            // Calcul de l'accélération sur chaque étoile
            e1.calcul_acceleration(fx / e1.getmass(), fy / e1.getmass());
            e2.calcul_acceleration(-fx / e2.getmass(), -fy / e2.getmass());
    
            // Mise à jour des positions
            e1.mise_a_jour_position(dt);
            e2.mise_a_jour_position(dt);
    
            // Stocker les positions pour le tracé
            positions_e1.push_back({e1.getx(), e1.gety()});
            positions_e2.push_back({e2.getx(), e2.gety()});
        
    

    
    }
}